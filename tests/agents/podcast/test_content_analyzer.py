"""
Content Analyzer 에이전트 테스트.

Content Analyzer가 사용자 입력에서 팟캐스트 에피소드 주제/테마/구조를
올바르게 추출하는지 검증한다.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from src.agents.podcast.content_analyzer import (
    ContentAnalyzerAgent,
    content_analyzer_agent,
    content_analyzer_node,
)
from src.models.agent_state import AgentState

# === 픽스처 ===


@pytest.fixture
def agent() -> ContentAnalyzerAgent:
    """테스트용 Content Analyzer 에이전트 인스턴스."""
    return ContentAnalyzerAgent()


@pytest.fixture
def base_state() -> AgentState:
    """기본 AgentState — 최소 필수 필드만 포함."""
    return AgentState(
        user_input="요즘 스트레스를 많이 받아서 마음이 힘들어요.",
        user_id="test_user_001",
        session_id="sess_test_001",
        mode="podcast",
    )


@pytest.fixture
def state_with_intent() -> AgentState:
    """Intent Classifier 결과가 포함된 AgentState."""
    return AgentState(
        user_input="요즘 스트레스를 많이 받아서 마음이 힘들어요.",
        user_id="test_user_001",
        session_id="sess_test_001",
        mode="podcast",
        intent={
            "primary_intent": "stress_relief",
            "complexity_score": 0.6,
        },
    )


@pytest.fixture
def mock_llm_response() -> dict[str, Any]:
    """LLM이 반환할 모의 분석 결과."""
    return {
        "topic": "스트레스 해소와 마음 돌봄",
        "themes": ["스트레스 관리", "자기돌봄", "감정 인식"],
        "episode_type": "reflection",
        "depth_level": "moderate",
        "target_audience": "직장인, 일상 스트레스를 겪는 20-40대",
        "suggested_structure": "공감 인트로 → 스트레스 원인 탐색 → 해소 방법 → 마무리 격려",
        "emotional_arc": "공감(시작) → 탐색(전개) → 안도(마무리)",
        "keywords": ["스트레스", "힘듦", "마음", "돌봄"],
    }


# === 단위 테스트 ===


class TestContentAnalyzerAgent:
    """Content Analyzer 에이전트 테스트 모음."""

    @pytest.mark.asyncio
    async def test_process_returns_content_analysis(
        self,
        agent: ContentAnalyzerAgent,
        base_state: AgentState,
        mock_llm_response: dict[str, Any],
    ) -> None:
        """process()가 content_analysis 필드를 올바르게 반환하는지 확인."""
        with patch.object(
            agent, "call_llm_json", new_callable=AsyncMock, return_value=mock_llm_response
        ):
            result = await agent.process(base_state)

        assert "content_analysis" in result
        assert result["content_analysis"]["topic"] == "스트레스 해소와 마음 돌봄"
        assert result["content_analysis"]["episode_type"] == "reflection"

    @pytest.mark.asyncio
    async def test_process_includes_intent_context(
        self,
        agent: ContentAnalyzerAgent,
        state_with_intent: AgentState,
        mock_llm_response: dict[str, Any],
    ) -> None:
        """Intent Classifier 결과가 있으면 참고 정보로 포함하는지 확인."""
        mock = AsyncMock(return_value=mock_llm_response)
        with patch.object(agent, "call_llm_json", mock):
            await agent.process(state_with_intent)

        # call_llm_json 호출 시 user_message에 Intent 분석 결과가 포함되어야 한다
        call_args = mock.call_args
        user_message = call_args.kwargs.get(
            "user_message", call_args.args[1] if len(call_args.args) > 1 else ""
        )
        assert "stress_relief" in user_message
        assert "0.6" in user_message

    @pytest.mark.asyncio
    async def test_process_without_intent(
        self,
        agent: ContentAnalyzerAgent,
        base_state: AgentState,
        mock_llm_response: dict[str, Any],
    ) -> None:
        """Intent가 없는 상태에서도 정상 동작하는지 확인."""
        mock = AsyncMock(return_value=mock_llm_response)
        with patch.object(agent, "call_llm_json", mock):
            result = await agent.process(base_state)

        assert "content_analysis" in result
        # Intent 참고 정보가 user_message에 포함되지 않아야 한다
        call_args = mock.call_args
        user_message = call_args.kwargs.get(
            "user_message", call_args.args[1] if len(call_args.args) > 1 else ""
        )
        assert "Intent Classifier" not in user_message

    @pytest.mark.asyncio
    async def test_process_only_returns_content_analysis_field(
        self,
        agent: ContentAnalyzerAgent,
        base_state: AgentState,
        mock_llm_response: dict[str, Any],
    ) -> None:
        """process()가 content_analysis 외 다른 필드를 반환하지 않는지 확인."""
        with patch.object(
            agent, "call_llm_json", new_callable=AsyncMock, return_value=mock_llm_response
        ):
            result = await agent.process(base_state)

        assert list(result.keys()) == ["content_analysis"]

    def test_agent_attributes(self, agent: ContentAnalyzerAgent) -> None:
        """에이전트 기본 속성이 올바르게 설정되는지 확인."""
        assert agent.name == "content_analyzer"
        assert agent.tier == 1


class TestContentAnalyzerNode:
    """LangGraph 노드 함수 테스트."""

    @pytest.mark.asyncio
    async def test_node_function_calls_agent(
        self,
        base_state: AgentState,
        mock_llm_response: dict[str, Any],
    ) -> None:
        """content_analyzer_node가 에이전트를 올바르게 호출하는지 확인."""
        with patch.object(
            content_analyzer_agent,
            "process",
            new_callable=AsyncMock,
            return_value={"content_analysis": mock_llm_response},
        ):
            result = await content_analyzer_node(base_state)

        assert "content_analysis" in result

"""
Learning Agent 테스트.

사용자 패턴 학습 분석, 백엔드 API 저장, 실패 시 안전한 처리를 검증한다.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from src.agents.shared.learning import (
    LearningAgent,
    learning_agent,
    learning_node,
)
from src.models.agent_state import AgentState

# === 픽스처 ===


@pytest.fixture
def agent() -> LearningAgent:
    """테스트용 Learning Agent 인스턴스."""
    return LearningAgent()


@pytest.fixture
def full_state() -> AgentState:
    """학습 분석에 필요한 모든 필드가 포함된 AgentState."""
    return AgentState(
        user_input="오늘 직장에서 스트레스를 많이 받았어요.",
        user_id="test_user_001",
        session_id="sess_test_001",
        mode="podcast",
        emotion_vectors={
            "primary_emotion": "stressed",
            "intensity": 0.7,
        },
        content_analysis={
            "topic": "직장 스트레스",
            "episode_type": "reflection",
        },
        final_output="오늘의 에피소드는 직장에서의 스트레스 관리에 대해 다룹니다...",
    )


@pytest.fixture
def minimal_state() -> AgentState:
    """최소한의 필드만 포함된 AgentState."""
    return AgentState(
        user_input="",
        user_id="test_user_001",
        session_id="sess_test_001",
        mode="podcast",
    )


@pytest.fixture
def mock_learning_data() -> dict[str, Any]:
    """LLM이 반환할 모의 학습 분석 결과."""
    return {
        "preferred_topics": ["직장 스트레스", "자기돌봄"],
        "emotion_patterns": {
            "dominant_emotion": "stressed",
            "expression_style": "직접적 표현",
            "trend": "stable",
        },
        "content_preferences": {
            "preferred_type": "reflection",
            "preferred_depth": "moderate",
            "preferred_tone": "warm",
        },
        "session_summary": "직장 스트레스에 대한 반성 세션",
        "improvement_notes": ["이완 기법 추가 추천"],
    }


# === 단위 테스트 ===


class TestLearningAgentProcess:
    """Learning Agent 핵심 로직 테스트."""

    @pytest.mark.asyncio
    async def test_process_returns_empty_dict(
        self,
        agent: LearningAgent,
        full_state: AgentState,
        mock_learning_data: dict[str, Any],
    ) -> None:
        """process()가 빈 dict를 반환하는지 확인 (AgentState 변경 없음)."""
        with (
            patch.object(
                agent, "call_llm_json", new_callable=AsyncMock, return_value=mock_learning_data
            ),
            patch.object(agent._api_client, "save", new_callable=AsyncMock),
        ):
            result = await agent.process(full_state)

        assert result == {}

    @pytest.mark.asyncio
    async def test_process_calls_llm_with_learning_context(
        self,
        agent: LearningAgent,
        full_state: AgentState,
        mock_learning_data: dict[str, Any],
    ) -> None:
        """LLM 호출 시 학습 컨텍스트가 올바르게 전달되는지 확인."""
        mock_llm = AsyncMock(return_value=mock_learning_data)
        with (
            patch.object(agent, "call_llm_json", mock_llm),
            patch.object(agent._api_client, "save", new_callable=AsyncMock),
        ):
            await agent.process(full_state)

        mock_llm.assert_called_once()
        call_args = mock_llm.call_args
        user_message = call_args.kwargs.get(
            "user_message", call_args.args[1] if len(call_args.args) > 1 else ""
        )
        # 컨텍스트에 사용자 입력이 포함되어야 한다
        assert "스트레스" in user_message

    @pytest.mark.asyncio
    async def test_process_calls_api_save(
        self,
        agent: LearningAgent,
        full_state: AgentState,
        mock_learning_data: dict[str, Any],
    ) -> None:
        """백엔드 API에 학습 결과를 저장하는지 확인."""
        mock_save = AsyncMock()
        with (
            patch.object(
                agent, "call_llm_json", new_callable=AsyncMock, return_value=mock_learning_data
            ),
            patch.object(agent._api_client, "save", mock_save),
        ):
            await agent.process(full_state)

        mock_save.assert_called_once()
        # 첫 번째 인자가 "learning" 리소스인지 확인
        call_args = mock_save.call_args
        assert call_args.args[0] == "learning" or call_args.kwargs.get("resource") == "learning"


class TestLearningAgentContext:
    """학습 컨텍스트 조합 테스트."""

    def test_build_context_with_full_state(
        self,
        agent: LearningAgent,
        full_state: AgentState,
    ) -> None:
        """모든 필드가 있을 때 컨텍스트가 올바르게 조합되는지 확인."""
        context = agent._build_learning_context(full_state)

        assert "[사용자 입력]" in context
        assert "스트레스" in context
        assert "[감정 분석]" in context
        assert "stressed" in context
        assert "[콘텐츠 분석]" in context
        assert "직장 스트레스" in context
        assert "[최종 출력 (요약)]" in context

    def test_build_context_with_minimal_state(
        self,
        agent: LearningAgent,
        minimal_state: AgentState,
    ) -> None:
        """최소 필드만 있을 때 기본 메시지를 반환하는지 확인."""
        context = agent._build_learning_context(minimal_state)

        assert context == "세션 데이터가 부족합니다."

    def test_build_context_truncates_long_output(
        self,
        agent: LearningAgent,
    ) -> None:
        """final_output이 길면 500자로 잘리는지 확인."""
        state = AgentState(
            user_input="테스트",
            user_id="u",
            session_id="s",
            mode="podcast",
            final_output="A" * 1000,
        )
        context = agent._build_learning_context(state)

        # 500자 + "..." 이 포함되어야 한다
        assert "..." in context
        assert "A" * 500 in context


class TestLearningAgentErrorHandling:
    """에러 처리 테스트."""

    @pytest.mark.asyncio
    async def test_api_save_failure_does_not_raise(
        self,
        agent: LearningAgent,
        full_state: AgentState,
        mock_learning_data: dict[str, Any],
    ) -> None:
        """API 저장 실패 시 예외가 전파되지 않는지 확인 (비동기 후처리)."""
        with (
            patch.object(
                agent, "call_llm_json", new_callable=AsyncMock, return_value=mock_learning_data
            ),
            patch.object(
                agent._api_client,
                "save",
                new_callable=AsyncMock,
                side_effect=Exception("저장 실패"),
            ),
        ):
            # 예외가 발생하지 않아야 한다
            result = await agent.process(full_state)

        assert result == {}

    def test_agent_attributes(self, agent: LearningAgent) -> None:
        """에이전트 기본 속성이 올바르게 설정되는지 확인."""
        assert agent.name == "learning"
        assert agent.tier is None  # 비동기 → TIER 없음


class TestLearningNode:
    """LangGraph 노드 함수 테스트."""

    @pytest.mark.asyncio
    async def test_node_function_calls_agent(
        self,
        full_state: AgentState,
    ) -> None:
        """learning_node가 에이전트를 올바르게 호출하는지 확인."""
        with patch.object(
            learning_agent,
            "process",
            new_callable=AsyncMock,
            return_value={},
        ):
            result = await learning_node(full_state)

        assert result == {}

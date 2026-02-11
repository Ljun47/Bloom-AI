"""
Learning Agent — 사용자 패턴 학습 에이전트 (비동기).

최종 에피소드 출력 후 비동기로 실행된다.
사용자의 상호작용 패턴(선호 주제, 감정 패턴, 대화 스타일)을 학습하고
결과를 백엔드 API로 저장한다.

양쪽 모드(대화/팟캐스트)에서 공용으로 사용되므로 shared에 배치.

담당: 개발자3
출력: 백엔드 API 저장 (AgentState에 직접 반영 없음)
모델: Haiku (경량)
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.agents.shared.base_agent import BaseAgent
from src.api.client import BackendClient
from src.api.contracts import SaveRequest
from src.models.agent_state import AgentState

# 시스템 프롬프트 — Learning Agent의 역할과 출력 형식
LEARNING_SYSTEM_PROMPT = """\
당신은 Mind-Log 플랫폼의 사용자 패턴 학습 분석가입니다.
이번 세션의 전체 처리 결과를 분석하여 사용자의 패턴을 요약합니다.

분석 항목:
1. 선호 주제: 사용자가 자주 다루는 주제 경향
2. 감정 패턴: 감정 표현 방식과 빈도
3. 콘텐츠 선호: 선호하는 에피소드 유형, 깊이, 구조
4. 개선 포인트: 다음 세션에서 개선할 수 있는 점

결과를 아래 JSON 형식으로 반환하세요. 반드시 유효한 JSON만 출력하세요.

{
    "preferred_topics": ["주제 1", "주제 2"],
    "emotion_patterns": {
        "dominant_emotion": "주요 감정",
        "expression_style": "감정 표현 스타일 설명",
        "trend": "stable | improving | declining"
    },
    "content_preferences": {
        "preferred_type": "education | conversation | meditation | story | reflection",
        "preferred_depth": "light | moderate | deep",
        "preferred_tone": "warm | informative | reflective"
    },
    "session_summary": "이번 세션 요약 (1-2문장)",
    "improvement_notes": ["개선 포인트 1", ...]
}
"""


class LearningAgent(BaseAgent):
    """
    사용자 패턴 학습 에이전트 (비동기).

    세션의 전체 처리 결과를 분석하여 사용자 패턴을 학습하고
    백엔드 API에 저장한다. AgentState에는 직접 반영하지 않는다.
    """

    def __init__(self) -> None:
        super().__init__(name="learning", tier=None)  # 비동기 — TIER 없음
        self._api_client = BackendClient()

    async def process(self, state: AgentState) -> dict[str, Any]:
        """
        세션 결과를 분석하여 사용자 패턴을 학습한다.

        입력: 전체 AgentState (읽기 전용)
        출력: 빈 dict (AgentState 변경 없음, 백엔드 API로만 저장)
        """
        user_id = state.get("user_id", "")
        session_id = state.get("session_id", "")
        mode = state.get("mode", "podcast")

        # 학습에 필요한 컨텍스트 조합
        learning_context = self._build_learning_context(state)

        # LLM으로 사용자 패턴 분석
        learning_data = await self.call_llm_json(
            system_prompt=LEARNING_SYSTEM_PROMPT,
            user_message=learning_context,
        )

        # 백엔드 API로 학습 결과 저장
        await self._save_learning_result(
            user_id=user_id,
            session_id=session_id,
            mode=mode,
            learning_data=learning_data,
        )

        # AgentState에는 변경 없음 (비동기 후처리)
        return {}

    def _build_learning_context(self, state: AgentState) -> str:
        """학습 분석에 필요한 세션 컨텍스트를 조합한다."""
        parts = []

        # 사용자 입력
        user_input = state.get("user_input", "")
        if user_input:
            parts.append(f"[사용자 입력]\n{user_input}")

        # 감정 분석 결과
        emotion = state.get("emotion_vectors", {})
        if emotion:
            parts.append(
                f"[감정 분석]\n"
                f"- 주요 감정: {emotion.get('primary_emotion', 'N/A')}\n"
                f"- 강도: {emotion.get('intensity', 'N/A')}"
            )

        # 콘텐츠 분석 결과
        content = state.get("content_analysis", {})
        if content:
            parts.append(
                f"[콘텐츠 분석]\n"
                f"- 주제: {content.get('topic', 'N/A')}\n"
                f"- 유형: {content.get('episode_type', 'N/A')}"
            )

        # 최종 출력
        final_output = state.get("final_output", "")
        if final_output:
            # 너무 길면 앞부분만 포함
            truncated = final_output[:500] + ("..." if len(final_output) > 500 else "")
            parts.append(f"[최종 출력 (요약)]\n{truncated}")

        return "\n\n".join(parts) if parts else "세션 데이터가 부족합니다."

    async def _save_learning_result(
        self,
        user_id: str,
        session_id: str,
        mode: str,
        learning_data: dict[str, Any],
    ) -> None:
        """학습 결과를 백엔드 API로 저장한다."""
        try:
            request = SaveRequest(
                user_id=user_id,
                session_id=session_id,
                type="learning",
                data={
                    "mode": mode,
                    "learning_data": learning_data,
                },
                timestamp=datetime.now(timezone.utc),
            )
            await self._api_client.save("learning", request)
            self.logger.info("학습 결과 저장 완료 (user=%s, session=%s)", user_id, session_id)

        except Exception as e:
            # 학습 저장 실패는 파이프라인을 중단하지 않는다 (비동기 후처리)
            self.logger.warning("학습 결과 저장 실패 — %s: %s", type(e).__name__, str(e))


# LangGraph 노드 함수로 사용할 에이전트 인스턴스
learning_agent = LearningAgent()


async def learning_node(state: AgentState) -> dict[str, Any]:
    """LangGraph 노드 — Learning Agent."""
    return await learning_agent(state)

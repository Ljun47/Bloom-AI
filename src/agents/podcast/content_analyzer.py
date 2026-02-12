"""
Content Analyzer — 팟캐스트 에피소드 콘텐츠 분석 에이전트.

TIER 1에서 Safety, Emotion, Podcast Reasoning과 병렬 실행된다.
대화모드의 Context Agent와 동일한 역할이며, 팟캐스트 에피소드에 맞게 특화되었다.

담당: 개발자3
출력 필드: content_analysis
모델: Sonnet 4
"""

from __future__ import annotations

from typing import Any

from src.agents.shared.base_agent import BaseAgent
from src.models.agent_state import AgentState

# 시스템 프롬프트는 prompts/podcast/content_analyzer.yaml에서 로드한다.
# BaseAgent의 get_prompt()로 접근.


class ContentAnalyzerAgent(BaseAgent):
    """
    팟캐스트 에피소드 콘텐츠 분석 에이전트.

    사용자 입력에서 에피소드 주제, 테마, 콘텐츠 요구사항을 추출한다.
    Intent Classifier의 의도 분류 결과를 참고하여 분석 정확도를 높인다.
    """

    def __init__(self) -> None:
        super().__init__(name="content_analyzer", tier=1)

    async def process(self, state: AgentState) -> dict[str, Any]:
        """
        사용자 입력을 분석하여 팟캐스트 에피소드 콘텐츠 구조를 추출한다.

        입력:
            - user_input: 사용자 원본 입력
            - intent: Intent Classifier의 의도 분류 결과 (선택적)

        출력:
            - content_analysis: 에피소드 주제, 테마, 구조 분석 결과
        """
        user_input = state["user_input"]
        intent = state.get("intent", {})

        # Intent Classifier 결과를 참고 정보로 포함
        context_info = ""
        if intent:
            context_info = (
                f"\n\n[참고 — Intent Classifier 분석 결과]\n"
                f"- 주요 의도: {intent.get('primary_intent', '미확인')}\n"
                f"- 복잡도: {intent.get('complexity_score', 'N/A')}\n"
            )

        # LLM 호출로 콘텐츠 분석 수행
        analysis = await self.call_llm_json(
            system_prompt=self.get_prompt("system_prompt"),
            user_message=f"사용자 입력: {user_input}{context_info}",
        )

        return {
            "content_analysis": analysis,
        }


# LangGraph 노드 함수로 사용할 에이전트 인스턴스
content_analyzer_agent = ContentAnalyzerAgent()


async def content_analyzer_node(state: AgentState) -> dict[str, Any]:
    """LangGraph 노드 — Content Analyzer."""
    return await content_analyzer_agent(state)

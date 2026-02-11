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

# 시스템 프롬프트 — Content Analyzer의 역할과 출력 형식을 정의
CONTENT_ANALYZER_SYSTEM_PROMPT = """\
당신은 Mind-Log 팟캐스트 플랫폼의 콘텐츠 분석 전문가입니다.
사용자의 입력을 분석하여 팟캐스트 에피소드를 위한 주제, 테마, 구조를 추출합니다.

분석 결과를 아래 JSON 형식으로 반환하세요. 반드시 유효한 JSON만 출력하세요.

{
    "topic": "에피소드 주제 (한 문장)",
    "themes": ["관련 테마 1", "관련 테마 2", ...],
    "episode_type": "education | conversation | meditation | story | reflection",
    "depth_level": "light | moderate | deep",
    "target_audience": "대상 청취자 설명",
    "suggested_structure": "추천 에피소드 구조 설명",
    "emotional_arc": "감정 흐름 제안 (시작 → 전개 → 마무리)",
    "keywords": ["핵심 키워드 1", "핵심 키워드 2", ...]
}

분석 시 고려사항:
- 사용자의 감정 상태와 의도를 파악하여 적절한 에피소드 유형을 결정
- 멘탈케어 맥락에 맞는 주제와 테마를 도출
- 청취자가 공감할 수 있는 감정 흐름을 설계
- 너무 무겁거나 가벼운 콘텐츠를 피하고 균형 잡힌 깊이를 추천
"""


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
            system_prompt=CONTENT_ANALYZER_SYSTEM_PROMPT,
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

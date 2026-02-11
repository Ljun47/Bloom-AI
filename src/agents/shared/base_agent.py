"""
BaseAgent — 모든 에이전트의 공통 부모 클래스.

에이전트마다 반복되는 공통 코드를 한 곳에 모아
코드 중복을 방지하고 프로토콜 규격 변경에 유연하게 대응한다.

포함 기능:
    - LLM 클라이언트 자동 초기화
    - 처리 시간 자동 측정 (audit.processing_time_ms)
    - 로깅 (에이전트명, TIER 정보)
    - 메시지 프로토콜 v2.0 엔벨로프 생성

각 에이전트는 이 클래스를 상속하고 process() 메서드만 구현하면 된다.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any

from src.agents.shared.llm_client import LLMClient
from src.models.agent_state import AgentState
from src.models.message import (
    MessageAudit,
    MessageEnvelope,
    MessageMetadata,
    MessageType,
    Priority,
)
from src.utils.logger import get_agent_logger


class BaseAgent(ABC):
    """
    모든 에이전트의 기본 클래스.

    Args:
        name: 에이전트 이름 (예: content_analyzer, batch_validator)
        tier: TIER 레벨 (0-4, 비동기/독립은 None)
        model_override: 설정 대신 직접 모델 ID를 지정할 때 사용

    사용 예시:
        class ContentAnalyzerAgent(BaseAgent):
            def __init__(self):
                super().__init__(name="content_analyzer", tier=1)

            async def process(self, state: AgentState) -> dict[str, Any]:
                # 에이전트 로직 구현
                return {"content_analysis": {...}}
    """

    def __init__(
        self,
        name: str,
        tier: int | None = None,
        model_override: str | None = None,
    ) -> None:
        self.name = name
        self.tier = tier
        self.logger = get_agent_logger(name)
        self.llm_client = LLMClient(
            agent_name=name,
            model_override=model_override,
        )
        # LLM 호출 횟수 추적 (audit용)
        self._llm_call_count = 0

    @abstractmethod
    async def process(self, state: AgentState) -> dict[str, Any]:
        """
        에이전트 핵심 로직.

        자기 담당 필드만 포함한 dict를 반환한다.
        LangGraph StateGraph가 반환된 dict를 기존 상태에 자동 merge한다.

        Args:
            state: 현재 AgentState (전체 상태 읽기 가능)

        Returns:
            업데이트할 필드만 포함한 dict
        """
        ...

    async def __call__(self, state: AgentState) -> dict[str, Any]:
        """
        LangGraph 노드 함수로 사용하기 위한 호출 인터페이스.

        처리 시간을 자동으로 측정하고 로깅한다.
        """
        tier_label = f"TIER {self.tier}" if self.tier is not None else "ASYNC"
        self.logger.info("[%s] %s 시작", tier_label, self.name)

        # LLM 호출 카운터 초기화
        self._llm_call_count = 0
        start_time = time.monotonic()

        try:
            result = await self.process(state)
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            self.logger.info(
                "[%s] %s 완료 (%dms, LLM %d회)",
                tier_label,
                self.name,
                elapsed_ms,
                self._llm_call_count,
            )
            return result

        except Exception as e:
            elapsed_ms = int((time.monotonic() - start_time) * 1000)
            self.logger.error(
                "[%s] %s 실패 (%dms) — %s: %s",
                tier_label,
                self.name,
                elapsed_ms,
                type(e).__name__,
                str(e),
            )
            raise

    async def call_llm(
        self,
        system_prompt: str,
        user_message: str,
        **kwargs: Any,
    ) -> str:
        """
        LLM 텍스트 생성 + 호출 횟수 자동 추적.

        process() 내에서 self.llm_client.generate() 대신 이 메서드를 사용하면
        audit.llm_calls가 자동으로 집계된다.
        """
        self._llm_call_count += 1
        return await self.llm_client.generate(
            system_prompt=system_prompt,
            user_message=user_message,
            **kwargs,
        )

    async def call_llm_json(
        self,
        system_prompt: str,
        user_message: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        LLM JSON 생성 + 호출 횟수 자동 추적.

        process() 내에서 self.llm_client.generate_json() 대신 이 메서드를 사용하면
        audit.llm_calls가 자동으로 집계된다.
        """
        self._llm_call_count += 1
        return await self.llm_client.generate_json(
            system_prompt=system_prompt,
            user_message=user_message,
            **kwargs,
        )

    def create_message(
        self,
        receiver: str,
        message_type: MessageType,
        payload: dict[str, Any],
        session_id: str,
        mode: str = "podcast",
        priority: Priority = Priority.HIGH,
    ) -> MessageEnvelope:
        """
        다른 에이전트에게 보낼 메시지 엔벨로프를 생성한다.

        독립 에이전트(Memory, Knowledge 등)에 요청을 보낼 때 사용한다.
        메시지 프로토콜 v2.0 규격을 자동으로 따른다.

        Args:
            receiver: 수신 에이전트 이름
            message_type: 메시지 유형 (request, response 등)
            payload: 요청/응답 데이터
            session_id: 세션 ID
            mode: 실행 모드 (conversation / podcast)
            priority: 메시지 우선순위

        Returns:
            프로토콜 v2.0 규격의 MessageEnvelope
        """
        return MessageEnvelope(
            sender=self.name,
            receiver=receiver,
            message_type=message_type,
            payload=payload,
            metadata=MessageMetadata(
                session_id=session_id,
                mode=mode,  # type: ignore[arg-type]
                interaction_unit="episode" if mode == "podcast" else "turn",
                tier=self.tier,
                priority=priority,
            ),
            audit=MessageAudit(
                processing_time_ms=0,
                llm_calls=self._llm_call_count,
                status="ok",
            ),
        )

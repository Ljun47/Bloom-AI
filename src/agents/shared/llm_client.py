"""
LLM 클라이언트 — Anthropic Claude API 래퍼.

모든 에이전트가 이 클라이언트를 통해 LLM을 호출한다.
모델 ID는 config/settings.yaml에서 관리하며, 환경변수로 오버라이드 가능.
API 모델이 변경되어도 이 파일과 설정 파일만 수정하면 된다.
"""

from __future__ import annotations

import json
from typing import Any

import anthropic

from config.loader import get_settings


class LLMClient:
    """
    Anthropic Claude API 비동기 클라이언트.

    에이전트별 모델과 파라미터를 설정에서 자동으로 가져온다.

    Args:
        agent_name: 에이전트 이름 (설정에서 모델/토큰/temperature 조회용)
        model_override: 설정 대신 직접 모델 ID를 지정할 때 사용

    사용 예시:
        client = LLMClient(agent_name="content_analyzer")
        result = await client.generate(
            system_prompt="너는 콘텐츠 분석가야.",
            user_message="오늘 기분이 안 좋아요.",
        )
    """

    def __init__(
        self,
        agent_name: str,
        model_override: str | None = None,
    ) -> None:
        settings = get_settings()
        agent_config = settings.get_agent_config(agent_name)

        # Anthropic 비동기 클라이언트 (API 키는 환경변수에서 자동 로드)
        self._client = anthropic.AsyncAnthropic()

        # 모델 설정 — 오버라이드 > 에이전트 설정 > 기본값
        self._model_id = model_override or agent_config.get(
            "model_id", settings.get_model_id("sonnet")
        )
        self._max_tokens: int = agent_config.get("max_tokens", 4096)
        self._temperature: float = agent_config.get("temperature", 0.7)

    @property
    def model_id(self) -> str:
        """현재 사용 중인 모델 ID."""
        return self._model_id

    async def generate(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        """
        텍스트 응답을 생성한다.

        Args:
            system_prompt: 시스템 프롬프트 (에이전트 역할 정의)
            user_message: 사용자 메시지 (처리할 입력)
            max_tokens: 최대 토큰 수 (None이면 에이전트 설정값 사용)
            temperature: 샘플링 온도 (None이면 에이전트 설정값 사용)

        Returns:
            LLM이 생성한 텍스트 응답
        """
        response = await self._client.messages.create(
            model=self._model_id,
            max_tokens=max_tokens or self._max_tokens,
            temperature=temperature or self._temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        # 첫 번째 content block에서 텍스트 추출 (TextBlock 가정)
        return response.content[0].text  # type: ignore[union-attr]

    async def generate_json(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> dict[str, Any]:
        """
        JSON 구조화된 응답을 생성한다.

        시스템 프롬프트에 JSON 형식을 요청하는 내용을 포함해야 한다.
        응답에서 JSON을 추출하여 dict로 파싱한다.

        Args:
            system_prompt: 시스템 프롬프트 (JSON 출력 형식 명시 필수)
            user_message: 사용자 메시지
            max_tokens: 최대 토큰 수
            temperature: 샘플링 온도

        Returns:
            파싱된 JSON dict

        Raises:
            json.JSONDecodeError: JSON 파싱 실패 시
        """
        raw_response = await self.generate(
            system_prompt=system_prompt,
            user_message=user_message,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        # JSON 블록 추출 시도 (```json ... ``` 형식 대응)
        return self._parse_json_response(raw_response)

    @staticmethod
    def _parse_json_response(text: str) -> dict[str, Any]:
        """
        LLM 응답에서 JSON을 추출한다.

        마크다운 코드 블록(```json ... ```)이나 순수 JSON 텍스트 모두 처리.
        """
        cleaned = text.strip()

        # 마크다운 JSON 코드 블록 제거
        if cleaned.startswith("```"):
            # 첫 번째 줄(```json)과 마지막 줄(```) 제거
            lines = cleaned.split("\n")
            # 시작 마커 제거
            if lines[0].startswith("```"):
                lines = lines[1:]
            # 끝 마커 제거
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        result: dict[str, Any] = json.loads(cleaned)
        return result

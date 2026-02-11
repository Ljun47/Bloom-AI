"""
설정 로더 — YAML 파일과 환경변수를 통합 관리.

사용법:
    from config.loader import get_settings
    settings = get_settings()
    model_id = settings.get_model_id("sonnet")
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, cast

import yaml
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

# 설정 파일 경로 (프로젝트 루트 기준)
_CONFIG_DIR = Path(__file__).parent
_SETTINGS_PATH = _CONFIG_DIR / "settings.yaml"


class Settings:
    """
    통합 설정 관리자.

    YAML 파일을 기본값으로 사용하고, 환경변수로 오버라이드할 수 있다.
    """

    def __init__(self, config_path: Path | None = None) -> None:
        """설정 파일을 로드한다."""
        path = config_path or _SETTINGS_PATH
        with open(path, encoding="utf-8") as f:
            self._config: dict[str, Any] = yaml.safe_load(f)

    @property
    def app_name(self) -> str:
        """앱 이름 반환."""
        return str(self._config["app"]["name"])

    @property
    def app_version(self) -> str:
        """앱 버전 반환."""
        return str(self._config["app"]["version"])

    # --- LLM 설정 ---

    def get_model_id(self, model_key: str) -> str:
        """
        모델 키에 해당하는 실제 모델 ID를 반환한다.

        환경변수 LLM_MODEL_{KEY}로 오버라이드 가능.
        예: LLM_MODEL_SONNET=claude-sonnet-4-20250514

        Args:
            model_key: 모델 키 (haiku, sonnet, opus)

        Returns:
            모델 ID 문자열
        """
        # 환경변수 오버라이드 확인
        env_key = f"LLM_MODEL_{model_key.upper()}"
        env_value = os.getenv(env_key)
        if env_value:
            return env_value

        return str(self._config["llm"]["models"][model_key])

    def get_agent_config(self, agent_name: str) -> dict[str, Any]:
        """
        에이전트별 설정을 반환한다.

        Args:
            agent_name: 에이전트 이름 (예: content_analyzer, batch_validator)

        Returns:
            에이전트 설정 dict (model, max_tokens, temperature 등)
        """
        agent_config = self._config.get("agents", {}).get(agent_name, {})

        # 모델 키를 실제 모델 ID로 변환
        if "model" in agent_config:
            model_key = agent_config["model"]
            agent_config = {**agent_config, "model_id": self.get_model_id(model_key)}

        # temperature가 없으면 기본값 사용
        if "temperature" not in agent_config:
            agent_config["temperature"] = self._config["llm"]["temperature"]["default"]

        # max_tokens가 없으면 기본값 사용
        if "max_tokens" not in agent_config:
            agent_config["max_tokens"] = self._config["llm"]["default_max_tokens"]

        return cast(dict[str, Any], agent_config)

    # --- 파이프라인 설정 ---

    @property
    def max_retries(self) -> int:
        """파이프라인 TIER 3 → TIER 2 재시도 상한."""
        return int(self._config["pipeline"]["max_retries"])

    @property
    def tier1_timeout(self) -> int:
        """TIER 1 병렬 작업 타임아웃 (초)."""
        return int(self._config["pipeline"]["tier1_timeout_seconds"])

    # --- API 설정 ---

    @property
    def api_base_url(self) -> str:
        """백엔드 API 기본 URL. 환경변수 BACKEND_API_URL로 설정."""
        return os.getenv("BACKEND_API_URL", "http://localhost:8000/api/v1")

    @property
    def api_timeout(self) -> int:
        """API 기본 타임아웃 (초)."""
        return int(self._config["api"]["timeout"])

    @property
    def api_max_retries(self) -> int:
        """API 최대 재시도 횟수."""
        return int(self._config["api"]["max_retries"])

    # --- 기능 플래그 ---

    def is_feature_enabled(self, feature_name: str) -> bool:
        """기능 플래그 확인. 환경변수 ENABLE_{FEATURE}로 오버라이드 가능."""
        env_key = f"ENABLE_{feature_name.upper()}"
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value.lower() in ("true", "1", "yes")

        return bool(self._config.get("features", {}).get(feature_name, False))

    # --- Anthropic API 키 ---

    @property
    def anthropic_api_key(self) -> str | None:
        """Anthropic API 키. 환경변수에서만 가져온다 (보안)."""
        return os.getenv("ANTHROPIC_API_KEY")


# 싱글톤 인스턴스 (모듈 레벨에서 한 번만 로드)
_settings_instance: Settings | None = None


def get_settings() -> Settings:
    """설정 싱글톤 인스턴스를 반환한다."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance

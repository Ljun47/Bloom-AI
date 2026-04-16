"""
BackendClient 단위 테스트.

httpx.AsyncClient를 mock하여 실제 HTTP 호출 없이
save/load 메서드의 요청 직렬화, 응답 파싱, 에러 핸들링을 검증.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.api.contracts import LoadResponse, SaveRequest, SaveResponse

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_httpx_client():
    """httpx.AsyncClient를 mock한 객체."""
    client = AsyncMock()
    client.aclose = AsyncMock()
    return client


@pytest.fixture
def backend_client(mock_httpx_client):
    """BackendClient 인스턴스 (httpx 클라이언트를 mock으로 교체)."""
    with patch("src.api.client.httpx.AsyncClient", return_value=mock_httpx_client):
        from src.api.client import BackendClient

        client = BackendClient(base_url="http://test-backend:8080/api")
        # 내부 _client를 mock으로 직접 교체
        client._client = mock_httpx_client
        return client


@pytest.fixture
def valid_save_request() -> SaveRequest:
    """유효한 SaveRequest fixture."""
    return SaveRequest(
        user_id="user_123",
        session_id="sess_abc123",
        type="podcast_episode",
        data={"turn": 1, "message": "안녕하세요"},
        timestamp=datetime.now(timezone.utc),
    )


def _make_response(status_code: int, json_data: dict[str, Any]) -> MagicMock:
    """httpx.Response mock 생성 헬퍼."""
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data
    response.raise_for_status = MagicMock()
    if status_code >= 400:
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            message=f"HTTP {status_code}",
            request=MagicMock(),
            response=response,
        )
    return response


# ---------------------------------------------------------------------------
# Tests: save()
# ---------------------------------------------------------------------------


class TestBackendClientSave:
    """BackendClient.save() 메서드 테스트."""

    @pytest.mark.asyncio
    async def test_save_success_and_serialization(
        self,
        backend_client,
        mock_httpx_client,
        valid_save_request,
    ) -> None:
        """정상적인 save 요청 시 SaveResponse 반환 + 올바른 직렬화 확인."""
        mock_httpx_client.post = AsyncMock(
            return_value=_make_response(
                200,
                {
                    "success": True,
                    "id": "saved_001",
                    "message": "saved",
                },
            ),
        )

        result = await backend_client.save("podcast_episodes", valid_save_request)

        # SaveResponse 검증
        assert isinstance(result, SaveResponse)
        assert result.success is True
        assert result.id == "saved_001"

        # 직렬화 검증
        call_args = mock_httpx_client.post.call_args
        url = call_args[0][0]
        json_body = call_args[1]["json"]

        assert url == "http://test-backend:8080/api/podcast_episodes"
        assert json_body["user_id"] == "user_123"
        assert json_body["session_id"] == "sess_abc123"
        assert json_body["type"] == "podcast_episode"
        assert "data" in json_body
        assert "timestamp" in json_body

    @pytest.mark.asyncio
    async def test_save_http_error_raises(
        self,
        backend_client,
        mock_httpx_client,
        valid_save_request,
    ) -> None:
        """500 응답 시 httpx.HTTPStatusError 발생."""
        mock_httpx_client.post = AsyncMock(
            return_value=_make_response(
                500,
                {
                    "success": False,
                    "error": {"code": "SERVER_ERROR", "message": "내부 오류"},
                },
            ),
        )

        with pytest.raises(httpx.HTTPStatusError):
            await backend_client.save("learning", valid_save_request)


# ---------------------------------------------------------------------------
# Tests: load()
# ---------------------------------------------------------------------------


class TestBackendClientLoad:
    """BackendClient.load() 메서드 테스트."""

    @pytest.mark.parametrize(
        "resource, kwargs, response_data, check",
        [
            (
                "learning",
                {"user_id": "user_123"},
                {
                    "success": True,
                    "data": [{"id": "1", "content": "데이터"}],
                    "total": 1,
                    "page": 1,
                },
                lambda r, _: (
                    isinstance(r, LoadResponse)
                    and r.success is True
                    and len(r.data) == 1
                    and r.total == 1
                ),
            ),
            (
                "podcast_episodes",
                {"user_id": "user_123", "type": "podcast_episode", "limit": 10},
                {"success": True, "data": [], "total": 0, "page": 1},
                lambda r, mock: (
                    r.data == []
                    and r.total == 0
                    and mock.get.call_args[1]["params"]["type"] == "podcast_episode"
                    and mock.get.call_args[1]["params"]["limit"] == 10
                ),
            ),
        ],
        ids=["success_with_data", "empty_with_query_params"],
    )
    @pytest.mark.asyncio
    async def test_load(
        self,
        backend_client,
        mock_httpx_client,
        resource,
        kwargs,
        response_data,
        check,
    ) -> None:
        """load 성공 + 쿼리 파라미터 전달 + 빈 결과 검증."""
        mock_httpx_client.get = AsyncMock(
            return_value=_make_response(200, response_data),
        )

        result = await backend_client.load(resource, **kwargs)

        assert check(result, mock_httpx_client)


# ---------------------------------------------------------------------------
# Tests: 리소스 관리
# ---------------------------------------------------------------------------


class TestBackendClientLifecycle:
    """BackendClient 리소스 관리 테스트."""

    @pytest.mark.asyncio
    async def test_lifecycle(
        self,
        backend_client,
        mock_httpx_client,
    ) -> None:
        """base_url 설정 확인 + close() 호출 시 리소스 정리 검증."""
        assert backend_client._base_url == "http://test-backend:8080/api"

        await backend_client.close()
        mock_httpx_client.aclose.assert_awaited_once()


# ---------------------------------------------------------------------------
# Tests: ingest_mind_frequencies() 로깅
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ingest_mind_frequencies_logs_on_success():
    """성공 시 INFO 레벨 로그가 남아야 한다."""
    from unittest.mock import MagicMock, patch

    from src.api.client import BackendClient

    client = BackendClient(base_url="http://test")
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()

    # 성공 시에도 예외 없이 완료됨
    with patch.object(client._client, "post", return_value=mock_resp):
        await client.ingest_mind_frequencies(
            session_id="s1", keywords=["번아웃"], description="힘든 하루"
        )


@pytest.mark.asyncio
async def test_ingest_mind_frequencies_logs_error_at_error_level():
    """실패 시 ERROR 레벨 로그가 남아야 한다 (WARNING 아님)."""
    from unittest.mock import patch

    from src.api.client import BackendClient

    client = BackendClient(base_url="http://test")

    # 실패 시에도 예외를 전파하지 않고 로그만 남김
    with patch.object(client._client, "post", side_effect=Exception("connection refused")):
        # 이 함수는 예외를 발생시키지 않음 (fire-and-forget)
        await client.ingest_mind_frequencies(
            session_id="s1", keywords=["번아웃"], description="힘든 하루"
        )


# ---------------------------------------------------------------------------
# Tests: _on_response 로그 하이브리드 (성공=헤더만, 에러=본문 포함)
# ---------------------------------------------------------------------------


class TestOnResponseLoggingHybrid:
    """_on_response 훅의 하이브리드 로깅 동작 검증.

    - 성공(2xx-3xx): response.text 호출 안 함, content-length 헤더만 사용
    - 에러(4xx-5xx): await response.aread() 후 response.text 호출하여 본문 로깅

    NOTE: src.api.client._logger는 propagate=False로 설정되어 caplog가 잡지 못한다.
          따라서 _logger를 직접 patch하여 호출 인자를 검증한다.
    """

    @pytest.mark.asyncio
    async def test_success_response_skips_body_read(self):
        """200 응답에서 본문 읽기 시도 없이 헤더만 로깅된다."""
        from src.api import client as client_module
        from src.api.client import BackendClient

        client = BackendClient(base_url="http://test")

        response = MagicMock(spec=httpx.Response)
        response.status_code = 200
        response.headers = httpx.Headers({"content-length": "42"})
        response.request = MagicMock()
        response.request.url = "http://test/resource"
        # text 속성 접근 시 실패 — 성공 응답에서 호출되면 안 됨
        type(response).text = property(
            lambda self: (_ for _ in ()).throw(AssertionError("text는 호출되면 안 됨"))
        )
        response.aread = AsyncMock()

        with patch.object(client_module, "_logger") as mock_logger:
            await client._on_response(response)

        # aread가 호출되지 않아야 함 (성공 응답은 본문 미수신)
        response.aread.assert_not_called()
        # info 레벨 1회 호출
        mock_logger.info.assert_called_once()
        call_kwargs = mock_logger.info.call_args
        extra = call_kwargs.kwargs["extra"]
        assert extra["status_code"] == 200
        # content-length 헤더 값 사용
        assert extra["content_length"] == 42
        # response_body 키가 extra에 없어야 함 (본문 미로깅)
        assert "response_body" not in extra

    @pytest.mark.asyncio
    async def test_error_response_reads_body(self):
        """500 응답에서 await aread() 후 본문이 로그에 포함된다."""
        from src.api import client as client_module
        from src.api.client import BackendClient

        client = BackendClient(base_url="http://test")

        response = MagicMock(spec=httpx.Response)
        response.status_code = 500
        response.headers = httpx.Headers({"content-type": "application/json"})
        response.request = MagicMock()
        response.request.url = "http://test/resource"
        response.text = '{"error":"internal server error","detail":"boom"}'
        response.aread = AsyncMock()

        with patch.object(client_module, "_logger") as mock_logger:
            await client._on_response(response)

        # 에러 응답은 명시적으로 본문 읽기
        response.aread.assert_awaited_once()
        mock_logger.error.assert_called_once()
        extra = mock_logger.error.call_args.kwargs["extra"]
        assert extra["status_code"] == 500
        assert "internal server error" in extra["response_body"]

    @pytest.mark.asyncio
    async def test_success_without_content_length_header(self):
        """Content-Length 헤더 없으면 content_length=None으로 안전 처리."""
        from src.api import client as client_module
        from src.api.client import BackendClient

        client = BackendClient(base_url="http://test")

        response = MagicMock(spec=httpx.Response)
        response.status_code = 201
        response.headers = httpx.Headers({})  # content-length 미포함
        response.request = MagicMock()
        response.request.url = "http://test/resource"
        response.aread = AsyncMock()

        with patch.object(client_module, "_logger") as mock_logger:
            await client._on_response(response)

        extra = mock_logger.info.call_args.kwargs["extra"]
        assert extra["content_length"] is None

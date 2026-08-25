import httpx
import pytest

from services.ingestion.http.client import SourceHttpClient
from services.ingestion.http.exceptions import (
    SourceInvalidContentError,
    SourceResponseError,
    SourceTimeoutError,
)


def test_successful_json_response_contains_request_id() -> None:
    captured_request_id: str | None = None

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal captured_request_id
        captured_request_id = request.headers.get("X-Request-ID")

        return httpx.Response(
            200,
            json={
                "frequency": 49.98,
            },
        )

    transport = httpx.MockTransport(handler)

    with SourceHttpClient(
        source="test_source",
        transport=transport,
        sleep_fn=lambda _: None,
    ) as client:
        data = client.get_json("https://example.test/grid")

    assert data == {"frequency": 49.98}
    assert captured_request_id is not None
    assert len(captured_request_id) > 0


def test_timeout_is_retried_and_raises_structured_error() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        raise httpx.ReadTimeout(
            "simulated timeout",
            request=request,
        )

    transport = httpx.MockTransport(handler)

    with SourceHttpClient(
        source="grid_india",
        max_attempts=3,
        backoff_seconds=0,
        transport=transport,
        sleep_fn=lambda _: None,
    ) as client:
        with pytest.raises(SourceTimeoutError) as exc_info:
            client.get_json("https://example.test/grid")

    error = exc_info.value

    assert attempts == 3
    assert error.source == "grid_india"
    assert error.url == "https://example.test/grid"
    assert error.request_id


def test_5xx_is_retried_and_then_succeeds() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            return httpx.Response(
                503,
                request=request,
            )

        return httpx.Response(
            200,
            json={"frequency": 49.99},
            request=request,
        )

    transport = httpx.MockTransport(handler)

    with SourceHttpClient(
        source="grid_india",
        max_attempts=3,
        backoff_seconds=0,
        transport=transport,
        sleep_fn=lambda _: None,
    ) as client:
        data = client.get_json("https://example.test/grid")

    assert attempts == 3
    assert data == {"frequency": 49.99}


def test_5xx_after_all_retries_raises_structured_error() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1

        return httpx.Response(
            503,
            request=request,
        )

    transport = httpx.MockTransport(handler)

    with SourceHttpClient(
        source="grid_india",
        max_attempts=3,
        backoff_seconds=0,
        transport=transport,
        sleep_fn=lambda _: None,
    ) as client:
        with pytest.raises(SourceResponseError) as exc_info:
            client.get_json("https://example.test/grid")

    error = exc_info.value

    assert attempts == 3
    assert error.status_code == 503
    assert error.source == "grid_india"
    assert error.request_id


def test_invalid_json_raises_structured_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            text="<html>This is not JSON</html>",
            headers={"Content-Type": "text/html"},
            request=request,
        )

    transport = httpx.MockTransport(handler)

    with SourceHttpClient(
        source="grid_india",
        transport=transport,
        sleep_fn=lambda _: None,
    ) as client:
        with pytest.raises(SourceInvalidContentError) as exc_info:
            client.get_json("https://example.test/grid")

    error = exc_info.value

    assert error.source == "grid_india"
    assert error.url == "https://example.test/grid"
    assert error.request_id

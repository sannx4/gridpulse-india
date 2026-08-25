import time
import uuid
from collections.abc import Callable
from typing import Any

import httpx

from services.ingestion.http.exceptions import (
    SourceInvalidContentError,
    SourceNetworkError,
    SourceResponseError,
    SourceTimeoutError,
)


class SourceHttpClient:
    RETRYABLE_STATUS_CODES = {
        500,
        502,
        503,
        504,
    }

    def __init__(
        self,
        *,
        source: str,
        timeout_seconds: float = 10.0,
        max_attempts: int = 3,
        backoff_seconds: float = 0.5,
        transport: httpx.BaseTransport | None = None,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be greater than 0")

        if backoff_seconds < 0:
            raise ValueError("backoff_seconds cannot be negative")

        self.source = source
        self.max_attempts = max_attempts
        self.backoff_seconds = backoff_seconds
        self.sleep_fn = sleep_fn

        self._client = httpx.Client(
            timeout=httpx.Timeout(timeout_seconds),
            transport=transport,
            follow_redirects=True,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "SourceHttpClient":
        return self

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        self.close()

    def get(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        request_id = str(uuid.uuid4())

        request_headers = dict(headers or {})
        request_headers["X-Request-ID"] = request_id

        last_timeout: httpx.TimeoutException | None = None
        last_network_error: httpx.RequestError | None = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                response = self._client.get(
                    url,
                    params=params,
                    headers=request_headers,
                )

            except httpx.TimeoutException as exc:
                last_timeout = exc

                if attempt < self.max_attempts:
                    self._sleep_before_retry(attempt)
                    continue

                raise SourceTimeoutError(
                    "Source request timed out",
                    source=self.source,
                    url=url,
                    request_id=request_id,
                ) from exc

            except httpx.RequestError as exc:
                last_network_error = exc

                if attempt < self.max_attempts:
                    self._sleep_before_retry(attempt)
                    continue

                raise SourceNetworkError(
                    "Source network request failed",
                    source=self.source,
                    url=url,
                    request_id=request_id,
                ) from exc

            if response.status_code in self.RETRYABLE_STATUS_CODES:
                if attempt < self.max_attempts:
                    self._sleep_before_retry(attempt)
                    continue

                raise SourceResponseError(
                    "Source returned a retryable server error",
                    source=self.source,
                    url=url,
                    request_id=request_id,
                    status_code=response.status_code,
                )

            if response.is_error:
                raise SourceResponseError(
                    "Source returned an HTTP error",
                    source=self.source,
                    url=url,
                    request_id=request_id,
                    status_code=response.status_code,
                )

            return response

        if last_timeout is not None:
            raise SourceTimeoutError(
                "Source request timed out",
                source=self.source,
                url=url,
                request_id=request_id,
            )

        if last_network_error is not None:
            raise SourceNetworkError(
                "Source network request failed",
                source=self.source,
                url=url,
                request_id=request_id,
            )

        raise RuntimeError("HTTP request terminated unexpectedly")

    def get_json(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        response = self.get(
            url,
            params=params,
            headers=headers,
        )

        request_id = response.request.headers["X-Request-ID"]

        try:
            return response.json()
        except ValueError as exc:
            raise SourceInvalidContentError(
                "Source response is not valid JSON",
                source=self.source,
                url=url,
                request_id=request_id,
            ) from exc

    def _sleep_before_retry(self, attempt: int) -> None:
        delay = self.backoff_seconds * (2 ** (attempt - 1))
        self.sleep_fn(delay)

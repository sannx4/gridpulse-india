class SourceHttpError(Exception):
    """Base exception for source HTTP failures."""

    def __init__(
        self,
        message: str,
        *,
        source: str,
        url: str,
        request_id: str,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.source = source
        self.url = url
        self.request_id = request_id

    def __str__(self) -> str:
        return (
            f"{self.message} [source={self.source}, url={self.url}, request_id={self.request_id}]"
        )


class SourceTimeoutError(SourceHttpError):
    """Raised when a source request exceeds its timeout."""


class SourceNetworkError(SourceHttpError):
    """Raised when the source cannot be reached because of a network failure."""


class SourceResponseError(SourceHttpError):
    """Raised when a source returns an unacceptable HTTP status."""

    def __init__(
        self,
        message: str,
        *,
        source: str,
        url: str,
        request_id: str,
        status_code: int,
    ) -> None:
        super().__init__(
            message,
            source=source,
            url=url,
            request_id=request_id,
        )
        self.status_code = status_code


class SourceInvalidContentError(SourceHttpError):
    """Raised when a source response cannot be parsed as expected."""

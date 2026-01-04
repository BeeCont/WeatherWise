from .base_exception import AppError, ErrorLayer, ErrorSeverity


class InfrastructureError(AppError):
    """Base class for errors related to infrastructure or external systems.

    This error type is used when something goes wrong outside the application
    itself — for example, network timeouts, unreachable services, or problems
    with external APIs.

    It extends AppError by adding an optional HTTP status code, which makes
    it useful for services and web applications.
    """
    default_code = ErrorLayer.NETWORK_ERROR
    default_message = "An infrastructure error occurred."
    default_http_status = 500

    def __init__(
            self, 
            message: str = None,
            *,
            severity: ErrorSeverity | None = None,
            code: ErrorLayer | None = None,
            http_status: int | None = None,
            details: dict | None = None
    ):
        """Create a new InfrastructureError instance.

        Args:
            message (str, optional): A human-readable message describing the error.
                If not provided, a default message is used.
            severity (ErrorSeverity, optional): How serious the error is.
                Defaults to the parent's default_severity.
            code (ErrorLayer, optional): Category of the error. Defaults to
                ErrorLayer.NETWORK_ERROR.
            http_status (int, optional): HTTP status code associated with the error.
                Defaults to default_http_status.
            details (dict, optional): Extra debugging information. Can contain
                request data, response data, IDs, or other useful metadata.
        """
        super().__init__(message, severity=severity, code=code, details=details)
        self.http_status = http_status or self.default_http_status

    def format_message(self) -> str:
        """Add the HTTP status to the formatted error message.

        The status is added after the main message line to show
        which HTTP code is associated with this error.
        """
        # Split the parent message into lines to insert HTTP status
        base = super().format_message().split("\n")

        # Insert HTTP status as a separate line after the main message
        base.insert(1, f" | http_status={self.http_status}")

        return "\n".join(base)


class HttpRequestError(InfrastructureError):
    """Error raised when an HTTP request fails.

    This error is used when the application cannot complete a request to
    an external service. It may happen because of timeouts, bad responses,
    wrong URLs, or connection problems.

    The default HTTP status for this error is 502 (Bad Gateway).
    """
    default_message = "An HTTP request error occurred."
    default_http_status = 502


class NetworkError(InfrastructureError):
    """Raised when a low-level network problem occurs.

    Examples include connection drops or DNS failures.
    The default HTTP status is 503."""

    default_message = "A network error occurred."
    default_http_status = 503


class JsonParseError(InfrastructureError):
    """Raised when JSON data cannot be parsed.

    This usually means the input is malformed or the response format
    is not what the application expected. Uses PARSE_ERROR and status 500.
    """
    default_code = ErrorLayer.PARSE_ERROR
    default_message = "A JSON parsing error occurred."
    default_http_status = 500
from enum import Enum
from datetime import datetime

class ErrorSeverity(Enum):
    """Severity levels that describe how important an error is.

    These levels can be used to filter logs and decide how to react.

    Attributes:
        INFO: General information, not a real problem.
        WARNING: Recoverable situations that may require attention.
        ERROR: A real problem that should be fixed.
        CRITICAL: A serious failure that may require stopping the application.
    """
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ErrorLayer(Enum):
    """Categories that describe where an error comes from.

    This helps developers understand and group errors during debugging.

    Attributes:
        APP_ERROR: A general application error.
        NETWORK_ERROR: Problems with network communication.
        PARSE_ERROR: Errors while reading or converting data.
        VALIDATION_ERROR: Input or data validation failures.
        DOMAIN_ERROR: Errors related to business rules or logic.
    """
    APP_ERROR = "APP_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    PARSE_ERROR = "PARSE_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    DOMAIN_ERROR = "DOMAIN_ERROR"

class AppError(Exception):
    """Base class for application-specific errors.

    AppError allows you to create structured errors that include a message,
    a severity level, a category, and optional details. It also supports
    exception chaining to show the original cause of the problem.

    Default attributes:
        default_code (ErrorLayer): Default error category.
        default_message (str): Default message when no message is provided.
        default_severity (ErrorSeverity): Default severity level.

    Example:
        >>> err = AppError(
        ...     "Failed to process request",
        ...     code=ErrorLayer.VALIDATION_ERROR,
        ...     severity=ErrorSeverity.WARNING
        ... )
        >>> print(err)
        2025-01-01 12:00:00 [VALIDATION_ERROR] [WARNING] Failed to process request
    """
    default_code = ErrorLayer.APP_ERROR
    default_message = "An application error occurred."
    default_severity = ErrorSeverity.ERROR

    def __init__(
            self, 
            message: str = None,
            *,
            severity: ErrorSeverity | None = None,
            code: ErrorLayer | None = None,
            details: dict | None = None
    ):
        """Create a new AppError instance.

        Args:
            message (str, optional): The main error message. If not provided,
                the default message is used.
            severity (ErrorSeverity, optional): How serious the error is.
                Uses the default severity if not set.
            code (ErrorLayer, optional): The type or category of the error.
                Uses the default code if not set.
            details (dict, optional): Extra information about the error.
                Useful for debugging (e.g., IDs, input data).

        Notes:
            You can use "raise ... from ..." to keep the original error as
            the cause of this error.
        """

        self.message = message or self.default_message
        self.severity = severity or self.default_severity
        self.code = code or self.default_code
        self.details = details or None
        self.created_at = datetime.now() # Timestamp when the error was created
        super().__init__(self.message)

    def format_message(self) -> str:
        """Build a readable multi-line message describing the error.

        The message includes:
            - a timestamp
            - error category
            - severity level
            - the main message
            - optional extra details
            - information about the original cause (if any)

        This method is useful for logs and debugging.

        Returns:
            str: A formatted message showing full error information.

        Example:
            >>> err = AppError("Invalid response")
            >>> print(err.format_message())
            2025-01-01 12:00:00 [APP_ERROR] [ERROR] Invalid response
        """
        timestamp = self.created_at.strftime("%Y-%m-%d %H:%M:%S") # Format timestamp to readable string
        base_message = [f"{timestamp} [{self.code.value}] [{self.severity.value}] {self.message}"]
            
        if self.details:
            base_message.append(f" | details = {self.details}")

        cause = getattr(self, '__cause__', None)

        if cause:
            if isinstance(cause, AppError):
                base_message.append(f"Caused by: {cause.format_message()}")
            else:
                base_message.append(f"Caused by: {repr(cause)}")

        return "\n".join(base_message) # Join all parts into a single string format

    def __str__(self) -> str:
        """Return the formatted error message.

        This makes AppError easy to print or log without calling
        format_message() directly.
        """
        return self.format_message()
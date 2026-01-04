from .base_exception import AppError, ErrorLayer


class DomainError(AppError):
    """Base class for domain-related errors.
    
    This error type is used for issues in the application's business logic
    such as validation failures, rule violations or invalid states in domain models.
    (e.g., invalid data that passes technical checks, but fails business rules).
    
    It extends from AppError without adding specific attributes or fields, focusing instead
    on logical errors."""
    default_code = ErrorLayer.DOMAIN_ERROR
    default_message = "A domain error occurred."

class InvalidWeatherDataError(DomainError):
    """Raised when weather data violates business rules after technical validation.

    This is for logical inconsistencies, such as temperature below absolute zero
    or other unrealistic values that pass schema validation but fail domain rules.

    Example usage in _parse_openweather_response:
        if weather_data.main.temp < -273.15:
            raise InvalidWeatherDataError(invalid_values={'temp': weather_data.main.temp})
    """
    default_code = ErrorLayer.VALIDATION_ERROR
    default_message = "Invalid weather data received (does not meet business rules)."

class InvalidCoordinatesError(DomainError):
    """Raised when coordinates are invalid according to domain rules.

    This exception is used when latitude or longitude values are outside
    acceptable ranges or formats.

    Example:
        if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
            raise InvalidCoordinatesError(invalid_values={'lat': latitude, 'lon': longitude})
    """
    default_code = ErrorLayer.VALIDATION_ERROR
    default_message = "Invalid coordinates received."
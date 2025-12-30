from .infrastructure_exceptions import InfrastructureError
from .base_exception import ErrorLayer


class WeatherServiceError(InfrastructureError):
    default_message = "Failed to retrieve weather data from weather service."
    default_http_status = 502  # Bad Gateway

class OpenWeatherServiceError(WeatherServiceError):
    default_message = "Failed to retrieve weather data from OpenWeather service."
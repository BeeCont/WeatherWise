from typing import Optional
import requests

class IPLocatorError(Exception):
    """Base exception for IP location retrieval errors."""

    def __init__(self, message="Error while fetching IP location data."):
        self.message = message
        super().__init__(self.message)

class OpenWeatherServiceError(Exception):
    """Base exception for OpenWeather service errors."""

    def __init__(self, message="Error while fetching OpenWeather data."):
        self.message = message
        super().__init__(self.message)
        
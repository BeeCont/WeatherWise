import requests
from requests.exceptions import RequestException

from .base_location import BaseLocation
from entities.coordinates import Coordinates
from exceptions.locator_exceptions import IPLocatorError
from exceptions.domain_exceptions import DomainError, InvalidCoordinatesError
from mixins.http_json_mixin import HttpJsonMixin
from exceptions.infrastructure_exceptions import (
    InfrastructureError, HttpRequestError, JsonParseError
)


class IPLocator(BaseLocation, HttpJsonMixin):
    """
    Service class for retrieving geographical coordinates based on an IP address.

    This class interacts with an external IP location service via HTTP requests,
    parses the JSON response, and converts it into a `Coordinates` object
    containing latitude and longitude.

    Exception Handling:
    - Low-level errors (network issues, HTTP errors, JSON parsing) are wrapped in
      `InfrastructureError`.
    - Domain-level issues (missing or invalid coordinates) raise `InvalidCoordinatesError`.
    - All exceptions are exposed to the caller as `IPLocatorError` with proper
      exception chaining via `__cause__`.

    Attributes:
        ip_url (str): URL of the IP location service endpoint.
    """

    def __init__(self, ip_url: str):
        """
        Initialize IPLocator with the target service URL.

        Args:
            ip_url (str): URL of the IP location service.
        """
        self.ip_url = ip_url

    def get_coordinates(self) -> Coordinates:
        """
        Retrieve coordinates for the current IP address.

        Sends an HTTP request to the configured IP service, parses the response,
        and converts it into a `Coordinates` object.

        Raises:
            IPLocatorError: If any error occurs during request, parsing, or validation.
        """
        try:
            data = self._make_http_request(self.ip_url)
            return self._parse_coordinates(data)
        except (InfrastructureError, DomainError) as e:
            raise IPLocatorError(
                message="Failed to get coordinates from IP location service."
            ) from e

    def _parse_coordinates(self, data: dict) -> Coordinates:
        """
        Convert JSON data into a `Coordinates` object.

        Args:
            data (dict): JSON data from IP location service.

        Raises:
            InvalidCoordinatesError: If latitude or longitude is missing or invalid.

        Returns:
            Coordinates: Object containing latitude and longitude.
        """
        try:
            latitude = float(data['lat'])
            longitude = float(data['lon'])
            return Coordinates(latitude=latitude, longitude=longitude)
        except (KeyError, ValueError) as e:
            raise InvalidCoordinatesError(
                f"Error parsing coordinates.",
                details={"lat": data.get('lat'), "lon": data.get('lon')}
            ) from e

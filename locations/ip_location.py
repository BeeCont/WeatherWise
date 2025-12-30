import requests
from requests.exceptions import RequestException

from .base_location import BaseLocation
from entities.coordinates import Coordinates
from exceptions.locator_exceptions import IPLocatorError
from exceptions.domain_exceptions import DomainError, InvalidCoordinatesError
from exceptions.infrastructure_exceptions import (
    InfrastructureError, HttpRequestError, JsonParseError
)


class IPLocator(BaseLocation):
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
            data = self._make_request()
            return self._parse_coordinates(data)
        except (InfrastructureError, DomainError) as e:
            raise IPLocatorError(
                message="Failed to get coordinates from IP location service."
            ) from e

    def _make_request(self) -> dict:
        """
        Send the HTTP request to the IP location service and check the response.

        Raises:
            InfrastructureError: Wraps network-level or response-related issues.
        
        Returns:
            dict: Parsed JSON response from the service.
        """
        try:
            response = requests.get(self.ip_url)
            return self._check_response(response)
        except (RequestException, HttpRequestError, JsonParseError) as e:
            raise InfrastructureError(
                message="Error during IP location request."
            ) from e

    def _check_response(self, response: requests.Response) -> dict:
        """
        Validate HTTP response status and parse JSON content.

        Args:
            response (requests.Response): HTTP response object.

        Raises:
            HttpRequestError: If HTTP status code is not 200.

        Returns:
            dict: Parsed JSON response.
        """
        if response.status_code != 200:
            raise HttpRequestError(
                message="Failed to retrieve valid data from the IP location service.",
                http_status=response.status_code
            )
        return self._parse_json(response)

    def _parse_json(self, response: requests.Response) -> dict:
        """
        Parse the HTTP response body as JSON.

        Args:
            response (requests.Response): HTTP response object.

        Raises:
            JsonParseError: If response cannot be parsed as JSON.

        Returns:
            dict: Parsed JSON data.
        """
        try:
            return response.json()
        except ValueError as e:
            preview = response.text[:100]  # Include first 100 chars for context
            raise JsonParseError(
                message="Failed to parse JSON response from IP location service.",
                http_status=response.status_code,
                details={"response_preview": preview}
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

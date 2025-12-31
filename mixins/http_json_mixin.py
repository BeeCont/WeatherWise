from typing import Any

import requests
from requests.exceptions import RequestException

from exceptions.infrastructure_exceptions import InfrastructureError, JsonParseError, HttpRequestError

class HttpJsonMixin:
    """Mixin for handling HTTP requests and JSON parsing.

    This mixin provides methods to perform HTTP GET requests, check responses,
    and parse JSON. It can be used in services that need to fetch and process
    JSON data from APIs.

    Usage:
        class MyService(HttpJsonMixin):
            def fetch_data(self):
                url = "https://example.com/api"
                data = self._make_http_request(url)
                proces_data...
    """

    def _make_http_request(self, url: str) -> dict[str, Any]:
        """Execute an HTTP GET request and return parsed JSON data.

        This method performs an HTTP GET request to the given URL, 
        validates the response status, and parses the response body as JSON.

        Args:
            url (str): The URL to send the GET request to.

        Raises:
            InfrastructureError: If there is an issue with the request.

        Returns:
            dict[str, Any]: The JSON response from the API.
        """
        try:
            response = requests.get(url)
            return self._check_http_response(response)
        except (RequestException, HttpRequestError, JsonParseError) as e:
            raise InfrastructureError(message="Error during HTTP API request.") from e

    def _check_http_response(self, response: requests.Response) -> dict[str, Any]:
        """Checks the status code of the response and returns JSON if successful.

        Args:
            response (requests.Response): The HTTP response object from the API request.

        Raises:
            HttpRequestError: If the response status is not 200.

        Returns:
            dict[str, Any]: Parsed JSON data.
        """
        if response.status_code != 200:
            raise HttpRequestError(
                message="Failed to retrieve valid data from the API.",
                http_status=response.status_code
            )
        
        return self._parse_json_response(response)

    def _parse_json_response(self, response: requests.Response) -> dict[str, Any]:
        """Attempts to parse the API response into a JSON object.

        This method tries to convert the response body into a JSON format.

        Args:
            response (requests.Response): The HTTP response object from the API request.

        Raises:
            JsonParseError: If the response cannot be parsed into JSON.

        Returns:
            dict[str, Any]: The parsed JSON data from the API response.
        """
        try:
            return response.json()
        except ValueError as e:
            preview = response.text[:100]  # Get first 100 characters for context

            raise JsonParseError(
                message="Failed to parse JSON response from API.",
                http_status=response.status_code,
                details={"response_preview": preview}
            ) from e
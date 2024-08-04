import requests
from requests.exceptions import RequestException

from .base_location import BaseLocation
from entities.coordinates import Coordinates
from exceptions.exceptions import IPLocatorError

class IPLocator(BaseLocation):
    '''
    A class to locate IP address coordinates using an external service.

    This class handles sending requests to an IP location service and 
    parsing the response to extract latitude and longitude coordinates. 
    '''
    def __init__(self, ip_url: str):
        # URL for the resource that will determine coordinates based on IP
        self.ip_url = ip_url

    def get_coordinates(self) -> Coordinates:
        # The main method for getting coordinates.
        try:
            # Fetch data and extract coordinates
            data = self._make_request()
            return self._parse_coordinates(data)
        except IPLocatorError as e:
            raise IPLocatorError(f"Failed to get coordinates: {str(e)}")

    def _make_request(self) -> dict:
        try:
            # Send request and check response
            return self._check_response(requests.get(self.ip_url))
        except RequestException as e:
            raise IPLocatorError(f"Error while executing request: {str(e)}. Check your internet connection.")

    def _check_response(self, response: requests.Response) -> dict:
        # Checks the status of the response code and returns JSON if the status is 200.
        if response.status_code != 200:
            print(response.status_code)
            raise IPLocatorError(f"HTTP request error. Status code: {response.status_code}")
        return self._parse_json(response)

    def _parse_json(self, response: requests.Response) -> dict:
        # Tries to convert the response to JSON format.
        try:
            return response.json()
        except ValueError as e:
            raise IPLocatorError(f"JSON parsing error: {str(e)}")

    def _parse_coordinates(self, data: dict) -> Coordinates:
        # Converts the IP response dictionary to a Coordinates object.
        try:
            latitude = float(data['lat'])
            longitude = float(data['lon'])
            return Coordinates(latitude=latitude, longitude=longitude)
        except (KeyError, ValueError) as e:
            raise IPLocatorError(f"Error parsing coordinates: {str(e)}")

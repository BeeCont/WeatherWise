import requests
import time
from requests.exceptions import RequestException

from .base_location import BaseLocation
from entities.coordinates import Coordinates
from exceptions.exceptions import IPLocatorError

class IPLocator(BaseLocation):
    def __init__(self, ip_url: str):
        self.ip_url = ip_url

    def get_coordinates(self) -> Coordinates:
        try:
            data = self._make_request()
            return self._parse_coordinates(data)
        except IPLocatorError as e:
            raise IPLocatorError(f"Failed to get coordinates: {str(e)}")

    def _make_request(self) -> dict:
        try:
            return self._check_response(requests.get(self.ip_url))
        except RequestException as e:
            raise IPLocatorError(f"Error while executing request: {str(e)}. Check your internet connection.")

    def _check_response(self, response: requests.Response) -> dict:
        if response.status_code != 200:
            print(response.status_code)
            raise IPLocatorError(f"HTTP request error. Status code: {response.status_code}")
        return self._parse_json(response)

    def _parse_json(self, response: requests.Response) -> dict:
        try:
            return response.json()
        except ValueError as e:
            raise IPLocatorError(f"JSON parsing error: {str(e)}")

    def _parse_coordinates(self, data: dict) -> Coordinates:
        try:
            latitude = float(data['lat'])
            longitude = float(data['lon'])
            return Coordinates(latitude=latitude, longitude=longitude)
        except (KeyError, ValueError) as e:
            raise IPLocatorError(f"Error parsing coordinates: {str(e)}")

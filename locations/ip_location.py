import requests

from .base_location import BaseLocation
from entities.coordinates import Coordinates
from config.settings import IP_URL

class IPLocation(BaseLocation):
    def get_coordinates(self) -> Coordinates:
        data = self._get_full_location_info()
        return Coordinates(latitude=data['lat'], longitude=data['lon'])

    def _get_full_location_info(self):
        response = requests.get(IP_URL)
        data = response.json()
        return data
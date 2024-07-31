import requests
import time
from requests.exceptions import RequestException
from typing import Literal
from datetime import datetime

from entities.coordinates import Coordinates
from entities.weather import Weather, WeatherType
from exceptions.exceptions import OpenWeatherServiceError
from config.settings import OPENWEATHER_URL_TEMPLATE

class OpenWeatherService:
    """
    Service to get weather data from OpenWeather API.

    Provides a method to request current weather by coordinates and convert
    the API response into a Weather object.
    """
    def __init__(self, locator: Coordinates):
        # Initializing the weather service with coordinates.
        self.locator = locator

    def get_weather(self) -> Weather:
        # The main method for getting weather data.
        try:
            data = self._make_request()
            return self._parse_openweather_response(data)
        except OpenWeatherServiceError as e:
            raise OpenWeatherServiceError(f'Failed to get weather: {str(e)}')

    def _make_request(self) -> dict:
        # Generates a URL and executes an HTTP GET request.
        try:
            url = OPENWEATHER_URL_TEMPLATE.format(
                latitude=self.locator.latitude, 
                longitude=self.locator.longitude
            )
            return self._check_response(requests.get(url))
        except RequestException as e:
            raise OpenWeatherServiceError(f'Error while executing request: {str(e)}. Check your internet connection.')

    def _check_response(self, response: requests.Response) -> dict:
        # Checks the status of the response code and returns JSON if the status is 200.
        if response.status_code != 200:
            print(response.status_code)
            raise OpenWeatherServiceError(f'HTTP request error. Status code: {response.status_code}.')
        return self._parse_json(response)

    def _parse_json(self, response: requests.Response) -> dict:
        # Tries to convert the response to JSON format.
        try:
            return response.json()
        except ValueError as e:
            raise OpenWeatherServiceError(f'JSON parsing error: {str(e)}.')
        
    def _parse_openweather_response(self, openweather_dict: dict) -> Weather:
        # Converts the OpenWeather response dictionary to a Weather object.
        try:
            return Weather(
                temperature=self._parse_temperature(openweather_dict),
                weather_type=self._parse_weather_type(openweather_dict),
                sunrise=self._parse_sun_time(openweather_dict, 'sunrise'),
                sunset=self._parse_sun_time(openweather_dict, 'sunset'),
                city=self._parse_city(openweather_dict)
            )
        except (KeyError, ValueError) as e:
            raise OpenWeatherServiceError(f'Error parsing weather data: {str(e)}.')
        
    def _parse_temperature(self, openweather_dict: dict) -> float:
        return round(openweather_dict['main']['temp'])
    
    def _parse_weather_type(self, openweather_dict: dict) -> WeatherType:
        # Find out the weather type by its ID and give back the right Weather Type.
        try:
            weather_type_id = str(openweather_dict['weather'][0]['id'])
        except (IndexError, KeyError) as e:
            raise OpenWeatherServiceError(f'Error parsing weather type: {str(e)}.')
        weather_types = {
            '1': WeatherType.THUNDERSTORM,
            '3': WeatherType.DRIZZLE,
            '5': WeatherType.RAIN,
            '6': WeatherType.SNOW,
            '7': WeatherType.FOG,
            '800': WeatherType.CLEAR,
            '80': WeatherType.CLOUDS
        }
        for _id, _weather_type in weather_types.items():
            if weather_type_id.startswith(_id):
                return _weather_type
        raise OpenWeatherServiceError

    def _parse_sun_time(
            self,
            openweather_dict: dict,
            time: Literal['sunrise', 'sunset']) -> datetime:
        # Turns the sunrise or sunset time from a timestamp.
        try:
            sun_time = openweather_dict['sys'][time]
            return datetime.fromtimestamp(sun_time)
        
        except(KeyError, TypeError) as e:
            raise OpenWeatherServiceError(f'Error parsing suntime: {str(e)}.')

    def _parse_city(self, openweather_dict: dict) -> str:
        try:
            return openweather_dict['name']
        except KeyError:
            raise OpenWeatherServiceError(f'Error parsing city.')
from datetime import datetime
from typing import Literal

import requests
from requests.exceptions import RequestException
from pydantic import ValidationError

from entities.coordinates import Coordinates
from entities.schemas.open_weather_schema import OpenWeatherSchema
from entities.dto.weather_dto import WeatherDTO
from exceptions.exceptions import OpenWeatherServiceError
from config.settings import OPENWEATHER_URL_TEMPLATE

class OpenWeatherService:
    """
    Service to get weather data from OpenWeather API.

    Provides a method to request current weather by coordinates and convert
    the API response into a WeatherDTO object.
    """
    def __init__(self, locator: Coordinates):
        #Initializing the weather service with coordinates.
        self.locator = locator

    def get_weather(self) -> WeatherDTO:
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
        
    def _parse_openweather_response(self, openweather_dict: dict) -> WeatherDTO:
        # Converts the OpenWeather response dictionary to a Weather object.
        try:
            weather_data = OpenWeatherSchema(**openweather_dict)
            return WeatherDTO(
                temp=self._parse_temperature(weather_data, 'temp'),
                feels_like=self._parse_temperature(weather_data, 'feels_like'),
                temp_min=self._parse_temperature(weather_data, 'temp_min'),
                temp_max=self._parse_temperature(weather_data, 'temp_max'),
                pressure=self._parse_pressure(weather_data),
                wind_speed=self._parse_wind_speed(weather_data),
                wind_dir=self._parse_wind_dir(weather_data),
                visibility_km=self._parse_visibility(weather_data),
                clouds=self._parse_clouds(weather_data),
                humidity=self._parse_humidity(weather_data),
                description=self._parse_description(weather_data),
                sunrise=self._parse_sun_time(weather_data, 'sunrise'),
                sunset=self._parse_sun_time(weather_data, 'sunset'),
                city_name=self._parse_city(weather_data)
            )
        except ValidationError as e:
            raise OpenWeatherServiceError(f'Error parsing weather data: {str(e)}.')
        
    def _parse_temperature(
            self, 
            weather_data: OpenWeatherSchema, 
            temp: Literal['temp', 'feels_like', 'temp_min', 'temp_max'] 
        ) -> float:
        return round(getattr(weather_data.main, temp))
    
    def _parse_pressure(self, weather_data: OpenWeatherSchema) -> int:
        return weather_data.main.pressure
    
    def _parse_wind_speed(self, weather_data: OpenWeatherSchema) -> float:
        return weather_data.wind.speed
    
    def _parse_wind_dir(self, weather_data: OpenWeatherSchema) -> str:
        deg = weather_data.wind.deg
        directions = [
            'North', 'North-East', 'East', 'South-East',
            'South', 'South-West', 'West', 'North-West'
        ]
        return directions[(deg // 45) % 8]
    
    def _parse_visibility(self, weather_data: OpenWeatherSchema) -> float:
        return weather_data.visibility / 1000
    
    def _parse_clouds(self, weather_data: OpenWeatherSchema) -> int:
        return weather_data.clouds.all
    
    def _parse_humidity(self, weather_data: OpenWeatherSchema) -> int:
        return weather_data.main.humidity
    
    def _parse_description(self, weather_data: OpenWeatherSchema) -> str:
        return weather_data.weather[0].description
    
    def _parse_sun_time(
            self,
            weather_data: OpenWeatherSchema,
            time: Literal['sunrise', 'sunset']) -> datetime:
        # Turns the sunrise or sunset time from a timestamp.
        return datetime.fromtimestamp(getattr(weather_data.sys, time))

    def _parse_city(self, weather_data: OpenWeatherSchema) -> str:
        return weather_data.name
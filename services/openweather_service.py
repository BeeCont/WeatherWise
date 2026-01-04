from datetime import datetime
from typing import Literal

import requests
from requests.exceptions import RequestException
from pydantic import ValidationError

from entities.coordinates import Coordinates
from entities.schemas.open_weather_schema import OpenWeatherSchema
from entities.dto.weather_dto import WeatherDTO
from exceptions.weather_service_exceptions import OpenWeatherServiceError
from exceptions.infrastructure_exceptions import InfrastructureError, JsonParseError, HttpRequestError
from exceptions.domain_exceptions import DomainError, InvalidWeatherDataError
from mixins.http_json_mixin import HttpJsonMixin
from config.settings import OPENWEATHER_URL_TEMPLATE

class OpenWeatherService(HttpJsonMixin):
    """Service to get weather data from OpenWeather API.

    This service provides an interface to query the current weather information
    by geographical coordinates (latitude and longitude) and converts the 
    API response into a structured `WeatherDTO` object that is easier to work with in
    the application.

    Usage:

        locator = Coordinates(latitude=51.5074, longitude=-0.1278)  # Coordinates for London
        weather_service = OpenWeatherService(locator)
        weather_data = weather_service.get_weather()

    The `WeatherDTO` object returned provides all the weather details in a 
    structured and easy-to-access format. 
    """
    def __init__(self, locator: Coordinates):
        """Initializing the weather service with coordinates.

        Args:
            locator (Coordinates): An instance of `Coordinates` that contains 
            the geographical coordinates (latitude and longitude) of the location.
        """
        self.locator = locator

    def get_weather(self) -> WeatherDTO:
        """Fetches the current weather data for the given coordinates.

        This method sends a request to the OpenWeather API, retrieves weather data,
        and converts it into a structure `WeatherDTO` object.

        Raises:
            OpenWeatherServiceError: If there is an issue with the request or response parsing.

        Returns:
            WeatherDTO: An object containing validated weather details such as temperature,
            wind speed, humidity, pressure, visibility, cloudiness, and other weather details.
        """
        try:
            url = OPENWEATHER_URL_TEMPLATE.format(
                latitude=self.locator.latitude, 
                longitude=self.locator.longitude
            )
            data = self._make_http_request(url)
            return self._parse_openweather_response(data)
        except (InfrastructureError, DomainError) as e:
            raise OpenWeatherServiceError(message="Failed to get weather data from OpenWeather service.") from e
        
    def _parse_openweather_response(self, openweather_dict: dict) -> WeatherDTO:
        """Converts the OpenWeather API into a structured WeatherDTO object.

        This method takes the raw response data from the OpenWeather API (in dictionary format),
        parse it, and returns a `WeatherDTO` object containing all the relevant weather information
        in a structured and accessible format.

        Args:
            openweather_dict (dict): The raw response data from the OpenWeather API in dictionary format.

        Raises:
            OpenWeatherServiceError: If there is an error during the parsing or mapping the response data.

        Returns:
            WeatherDTO: An object containing validated weather details such as temperature,
            wind speed, humidity, pressure, visibility, cloudiness, and other weather details.
        """
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
            raise InvalidWeatherDataError(f'Error parsing weather data: {str(e)}.')
        
    def _parse_temperature(
            self, 
            weather_data: OpenWeatherSchema, 
            temp: Literal['temp', 'feels_like', 'temp_min', 'temp_max'] 
        ) -> float:
        # Extracts and rounds temperature values.
        return round(getattr(weather_data.main, temp))
    
    def _parse_pressure(self, weather_data: OpenWeatherSchema) -> int:
        return weather_data.main.pressure
    
    def _parse_wind_speed(self, weather_data: OpenWeatherSchema) -> float:
        return weather_data.wind.speed
    
    def _parse_wind_dir(self, weather_data: OpenWeatherSchema) -> str:
        # Converts wind direction from degrees to a copmass direction.
        deg = weather_data.wind.deg
        directions = [
            'North', 'North-East', 'East', 'South-East',
            'South', 'South-West', 'West', 'North-West'
        ]
        return directions[(deg // 45) % 8]
    
    def _parse_visibility(self, weather_data: OpenWeatherSchema) -> float:
        # Converts visibility from meters to kilometers.
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
        # Converts sunrise or sunset time from a UNIX timestamp to a datetime object.
        return datetime.fromtimestamp(getattr(weather_data.sys, time))

    def _parse_city(self, weather_data: OpenWeatherSchema) -> str:
        return weather_data.name
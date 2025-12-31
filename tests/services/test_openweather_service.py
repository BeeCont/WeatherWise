import json
from datetime import datetime
from typing import Callable, Any

import pytest
from unittest.mock import MagicMock, patch
from requests.exceptions import RequestException

from entities.coordinates import Coordinates
from entities.dto.weather_dto import WeatherDTO
from exceptions.weather_service_exceptions import OpenWeatherServiceError
from exceptions.infrastructure_exceptions import HttpRequestError, JsonParseError, InfrastructureError
from exceptions.domain_exceptions import InvalidWeatherDataError
from services.openweather_service import OpenWeatherService
from config.settings import BASE_DIR

"""
Unit tests for the OpenWeatherService class.

This module contains a suite of tests to verify the functionality of the OpenWeatherService.
It covers:
- Successful retrieval and parsing of weather data.
- Handling of invalid data with validation errors.
- Processing missing fields in API responses.
- Calculation of wind directions based on degrees.
- Error handling for network request failures.
- Responses to invalid HTTP status codes.
- Parsing errors for invalid JSON.
- Initialization errors with incorrect coordinates.

These tests use mocking to isolate dependencies and ensure reliable, repeatable results.
"""

@pytest.fixture
def coordinates() -> Coordinates:
    """Fixture for New York coordinates.

    Returns a Coordinates instance with latitude and longitude for New York.
    """
    return Coordinates(latitude=40.7128, longitude=-74.0060)

@pytest.fixture
def service(coordinates: Coordinates) -> OpenWeatherService:
    """Fixture for OpenWeatherService instance.

    Creates an OpenWeatherService instance with the provided coordinates.
    """
    return OpenWeatherService(locator=coordinates)

@pytest.fixture
def base_successful_response() -> Callable[[str], Any]:
    """Fixture for loading JSON response from file.

    Returns a function that loads JSON from the specified file in the fixtures directory.
    """
    def _load_fixture(filename: str) -> Any:
        filepath = str(BASE_DIR) + f'/fixtures/{filename}'
        with open(filepath, 'r') as file:
            return json.load(file)
    return _load_fixture

def test_successful_weather_request(service: OpenWeatherService, base_successful_response: Callable[[str], Any]) -> None:
    """Test for successful request and weather data parsing.

    Verifies that the service correctly handles a successful API response and returns the expected WeatherDTO.
    """
    # Load correct data from fixtures
    mock_response = base_successful_response('openweather_success_response.json')
    
    # Create expected WeatherDTO based on fixture data
    expected_weather = WeatherDTO(
        temp=round(mock_response["main"]["temp"]),
        feels_like=round(mock_response["main"]["feels_like"]),
        temp_min=round(mock_response["main"]["temp_min"]),
        temp_max=round(mock_response["main"]["temp_max"]),
        pressure=mock_response["main"]["pressure"],
        humidity=mock_response["main"]["humidity"],
        wind_speed=mock_response["wind"]["speed"],
        wind_dir="East",  # Expected wind direction for deg=90
        visibility_km=mock_response["visibility"] / 1000,
        clouds=mock_response["clouds"]["all"],
        description=mock_response["weather"][0]["description"],
        sunrise=datetime.fromtimestamp(mock_response["sys"]["sunrise"]),
        sunset=datetime.fromtimestamp(mock_response["sys"]["sunset"]),
        city_name=mock_response["name"]
    )

    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        result = service.get_weather()
        assert result == expected_weather

def test_unsuccessful_weather_request(service: OpenWeatherService, base_successful_response: Callable[[str], Any]) -> None:
    """Test for handling invalid data with validation error.

    Verifies that the service raises OpenWeatherServiceError on invalid data,
    with the inner cause being InvalidWeatherDataError and appropriate message.
    """
    # Load correct data from fixtures
    mock_response = base_successful_response('openweather_success_response.json')
    
    # Assign invalid values to all fields to trigger validation errors
    mock_response['main']['temp'] = -120  # Invalid temperature (< -100)
    mock_response['main']['feels_like'] = -101  # Invalid feels_like temperature (< -100)
    mock_response['main']['temp_min'] = -150  # Invalid min temperature (< -100)
    mock_response['main']['temp_max'] = -140  # Invalid max temperature (< -100)
    mock_response['main']['pressure'] = -1  # Invalid pressure (<= 0)
    mock_response['main']['humidity'] = -1  # Invalid humidity (< 0)
    mock_response['wind']['speed'] = -10  # Invalid wind speed (< 0)
    mock_response['wind']['deg'] = -500  # Invalid wind degree (< 0)
    mock_response['visibility'] = -1000  # Invalid visibility (< 0)
    mock_response['clouds']['all'] = -10  # Invalid cloud cover (< 0)
    mock_response['weather'][0]['id'] = -1  # Invalid weather id (< 0)
    mock_response['weather'][0]['description'] = None  # Invalid weather description (not str)
    mock_response['sys']['sunrise'] = None  # Invalid sunrise timestamp (not int)
    mock_response['sys']['sunset'] = None  # Invalid sunset timestamp (not int)
    mock_response['name'] = 435345  # Invalid city name (not str)

    # Simulate the request with mock data
    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        # Assert that the service raises an error when invalid data is returned
        with pytest.raises(OpenWeatherServiceError) as exc_info:
            service.get_weather()

        assert exc_info.value.message == "Failed to get weather data from OpenWeather service."
        cause = exc_info.value.__cause__
        assert isinstance(cause, InvalidWeatherDataError)
        assert "Error parsing weather data:" in cause.message

def test_missing_fields(service: OpenWeatherService, base_successful_response: Callable[[str], Any]) -> None:
    """Test for handling missing fields with validation error.

    Verifies that the service raises OpenWeatherServiceError on missing required fields,
    with the inner cause being InvalidWeatherDataError and parsing error message.
    """
    mock_response = base_successful_response('openweather_success_response.json')

    del mock_response["main"]["temp"]  # Delete temperature (required field)
    del mock_response["wind"]["speed"]  # Delete wind speed (required field)
    del mock_response["weather"]  # Delete weather description (required list)

    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        with pytest.raises(OpenWeatherServiceError) as exc_info:
            service.get_weather()
        
        assert exc_info.value.message == "Failed to get weather data from OpenWeather service."
        cause = exc_info.value.__cause__
        assert isinstance(cause, InvalidWeatherDataError)
        assert "Error parsing weather data:" in cause.message

@pytest.mark.parametrize("degree, expected_direction", [
    (0, "North"), (44, "North"), (45, "North-East"), (89, "North-East"),
    (90, "East"), (134, "East"), (135, "South-East"), (179, "South-East"),
    (180, "South"), (224, "South"), (225, "South-West"), (269, "South-West"),
    (270, "West"), (314, "West"), (315, "North-West"), (359, "North-West"),
    (360, "North")
])
def test_wind_direction(degree: int, expected_direction: str, service: OpenWeatherService, base_successful_response: Callable[[str], Any]) -> None:
    """Parameterized test for wind direction calculation.

    Verifies that wind direction is correctly calculated based on degrees (deg).
    Covers all possible directions and boundary values.
    """
    mock_response = base_successful_response('openweather_success_response.json')
    mock_response['wind']['deg'] = degree  # Change default degree to parametrized value

    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        weather_data = service.get_weather()
        assert weather_data.wind_dir == expected_direction

def test_request_failure(service: OpenWeatherService) -> None:
    """Test for request failure (RequestException).

    Verifies that the service raises OpenWeatherServiceError on request error,
    with the inner cause being InfrastructureError and appropriate message.
    """
    with patch('requests.get', side_effect=RequestException):
        with pytest.raises(OpenWeatherServiceError) as exc_info:
            service.get_weather()
        assert exc_info.value.message == "Failed to get weather data from OpenWeather service."
        cause = exc_info.value.__cause__
        assert isinstance(cause, InfrastructureError)
        assert "Error during HTTP API request." in cause.message

def test_invalid_status_code(service: OpenWeatherService) -> None:
    """Test for invalid HTTP status code (non-200).

    Verifies that the service raises OpenWeatherServiceError on status 404,
    with the chain of causes including InfrastructureError and HttpRequestError with correct status.
    """
    with patch('requests.get', return_value=MagicMock(status_code=404)):
        with pytest.raises(OpenWeatherServiceError) as exc_info:
            service.get_weather()
        assert exc_info.value.message == "Failed to get weather data from OpenWeather service."
        infra_cause = exc_info.value.__cause__
        assert isinstance(infra_cause, InfrastructureError)
        http_cause = infra_cause.__cause__
        assert isinstance(http_cause, HttpRequestError)
        assert http_cause.http_status == 404

def test_invalid_json_response(service: OpenWeatherService) -> None:
    """Test for invalid JSON response (ValueError on parsing).

    Verifies that the service raises OpenWeatherServiceError on JSON parsing error,
    with the chain of causes including InfrastructureError and JsonParseError.
    """
    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(side_effect=ValueError))):
        with pytest.raises(OpenWeatherServiceError, match='Failed to get weather data from OpenWeather service.') as exc_info:
            service.get_weather()

        assert exc_info.value.message == "Failed to get weather data from OpenWeather service."
        infra_cause = exc_info.value.__cause__
        assert isinstance(infra_cause, InfrastructureError)
        json_cause = infra_cause.__cause__
        assert isinstance(json_cause, JsonParseError)

def test_incorrect_coordinates() -> None:
    """Test for incorrect coordinates (locator=None).

    Verifies that initializing the service with None raises AttributeError.
    """
    with pytest.raises(AttributeError, match="NoneType"):
        OpenWeatherService(locator=None).get_weather()
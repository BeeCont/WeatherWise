import json
from datetime import datetime
from typing import Callable, Any

import pytest
from unittest.mock import MagicMock, patch
from requests.exceptions import RequestException

from entities.coordinates import Coordinates
from entities.dto.weather_dto import WeatherDTO
from exceptions.exceptions import OpenWeatherServiceError
from services.openweather_service import OpenWeatherService
from config.settings import BASE_DIR

# Fixture for New York coordinates
@pytest.fixture
def coordinates() -> Coordinates:
    return Coordinates(latitude=40.7128, longitude=-74.0060)

# Fixture for OpenWeatherService with coordinates
@pytest.fixture
def service(coordinates: Coordinates) -> OpenWeatherService:
    return OpenWeatherService(locator=coordinates)

# Fixture to load JSON response from file
@pytest.fixture
def base_successful_response() -> Callable[[str], Any]:
    def _load_fixture(filename: str) -> Any:
        filepath = str(BASE_DIR) + f'/fixtures/{filename}'
        with open(filepath, 'r') as file:
            return json.load(file)
    return _load_fixture

# Test successful request and response parsing
def test_successful_weather_request(service: OpenWeatherService, base_successful_response: Callable[[str], Any]) -> None:
    # Load correct data from fixtures
    mock_response = base_successful_response('openweather_success_response.json')
    #Use fixtures data for creating expected data
    expected_weather = WeatherDTO(
        temp=round(mock_response["main"]["temp"]),
        feels_like=round(mock_response["main"]["feels_like"]),
        temp_min=round(mock_response["main"]["temp_min"]),
        temp_max=round(mock_response["main"]["temp_max"]),
        pressure=mock_response["main"]["pressure"],
        humidity=mock_response["main"]["humidity"],
        wind_speed=mock_response["wind"]["speed"],
        wind_dir="East",  # If the angle is 90 equal, "East" is expected
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

def test_unsuccess_weather_request(service: OpenWeatherService, base_successful_response: Callable[[str], Any]) -> None:
# Load correct data from fixtures
    mock_response = base_successful_response('openweather_success_response.json')
    
    # Assign invalid values to all fields
    mock_response['main']['temp'] = -120  # Invalid temperature
    mock_response['main']['feels_like'] = -101  # Invalid feels_like temperature
    mock_response['main']['temp_min'] = -150  # Invalid min temperature
    mock_response['main']['temp_max'] = -140  # Invalid max temperature
    mock_response['main']['pressure'] = -1  # Invalid pressure
    mock_response['main']['humidity'] = -1  # Invalid humidity
    mock_response['wind']['speed'] = -10  # Invalid wind speed
    mock_response['wind']['deg'] = -500  # Invalid wind degree
    mock_response['visibility'] = -1000  # Invalid visibility
    mock_response['clouds']['all'] = -10  # Invalid cloud cover
    mock_response['weather'][0]['id'] = -1  # Invalid weather id
    mock_response['weather'][0]['description'] = None  # Invalid weather description
    mock_response['sys']['sunrise'] = None  # Invalid sunrise timestamp
    mock_response['sys']['sunset'] = None  # Invalid sunset timestamp
    mock_response['name'] = 435345  # Invalid city name (should be a string)

    # Simulate the request with mock data
    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        # Assert that the service raises an error when invalid data is returned
        with pytest.raises(OpenWeatherServiceError, match='Error parsing weather data: 15'):
            service.get_weather()

# Test missing data
def test_missing_fields(service: OpenWeatherService, base_successful_response: Callable[[str], Any]) -> None:
    mock_response = base_successful_response('openweather_success_response.json')

    del mock_response["main"]["temp"]  # Delete temperature
    del mock_response["wind"]["speed"]  # Delete wind speed
    del mock_response["weather"]  # Delete weather description

    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        with pytest.raises(OpenWeatherServiceError, match="Error parsing weather data: 3"):
            service.get_weather()

# Test different wind degrees
@pytest.mark.parametrize("degree, expected_direction", [
    (0, "North"), (44, "North"), (45, "North-East"), (89, "North-East"), 
    (90, "East"), (134, "East"), (135, "South-East"), (179, "South-East"), 
    (180, "South"), (224, "South"), (225, "South-West"), (269, "South-West"), 
    (270, "West"), (314, "West"), (315, "North-West"), (359, "North-West"),
    (360, "North")
])
def test_wind_direction(degree: int, expected_direction: str, service: OpenWeatherService, base_successful_response: Callable[[str], Any]) -> None:
    mock_response = base_successful_response('openweather_success_response.json')
    mock_response['wind']['deg'] = degree # Change default degree to parametrize degree

    with patch('requests.get', return_value=MagicMock(status_code=200, json= MagicMock(return_value=mock_response))):
        weather_data = service.get_weather()
        assert weather_data.wind_dir == expected_direction

# Test request failure
def test_request_failure(service: OpenWeatherService) -> None:
    with patch('requests.get', side_effect=RequestException):
        with pytest.raises(OpenWeatherServiceError, match='Error while executing request.'):
            service.get_weather()

# Test invalid status code
def test_invalid_status_code(service: OpenWeatherService) -> None:
    with patch('requests.get', return_value=MagicMock(status_code=404)):
        with pytest.raises(OpenWeatherServiceError, match='HTTP request error. Status code: 404'):
            service.get_weather()

# Test invalid JSON response
def test_invalid_json_response(service: OpenWeatherService) -> None:
    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(side_effect=ValueError))):
        with pytest.raises(OpenWeatherServiceError, match='JSON parsing error.'):
            service.get_weather()

# Test incorrect coordinates
def test_incorrect_coordinates() -> None:
    with pytest.raises(AttributeError):
        OpenWeatherService(locator=None).get_weather()
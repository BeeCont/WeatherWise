import pytest
import json
from unittest.mock import MagicMock, patch
from datetime import datetime
from requests.exceptions import RequestException
from typing import Callable, Any

from entities.coordinates import Coordinates
from entities.weather import Weather, WeatherType
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
    mock_response = base_successful_response('openweather_success_response.json')
    expected_weather = Weather(
        temperature=23,
        weather_type=WeatherType.CLEAR,
        sunrise=datetime.fromtimestamp(1596242400),
        sunset=datetime.fromtimestamp(1596292800),
        city='New York'
    )

    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        result = service.get_weather()
        assert result == expected_weather

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

# Test missing temperature
def test_missing_temperature(service: OpenWeatherService, base_successful_response: Callable[[str], Any]) -> None:
    mock_response = base_successful_response('openweather_success_response.json')
    del mock_response['main']['temp']
    
    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        with pytest.raises(OpenWeatherServiceError, match='Error parsing weather data.'):
            service.get_weather()

# Test invalid temperature type
def test_invalid_temperature_type(service: OpenWeatherService, base_successful_response: Callable[[str], Any]) -> None:
    mock_response = base_successful_response('openweather_success_response.json')
    mock_response['main']['temp'] = 'invalid'
    
    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        with pytest.raises(OpenWeatherServiceError, match='Error parsing weather data.'):
            service.get_weather()

# Test invalid weather type
def test_invalid_weather_type(service: OpenWeatherService, base_successful_response: Callable[[str], Any]) -> None:
    mock_response = base_successful_response('openweather_success_response.json')
    mock_response['weather'][0]['id'] = 9999
    
    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        with pytest.raises(OpenWeatherServiceError, match='Unregistered weather type ID.'):
            service.get_weather()

# Test missing weather type
def test_missing_weather_type(service: OpenWeatherService, base_successful_response: Callable[[str], Any]) -> None:
    mock_response = base_successful_response('openweather_success_response.json')
    del mock_response['weather']
    
    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        with pytest.raises(OpenWeatherServiceError, match='Error parsing weather type.'):
            service.get_weather()

# Test missing sunrise
def test_missing_sunrise(service: OpenWeatherService, base_successful_response: Callable[[str], Any]) -> None:
    mock_response = base_successful_response('openweather_success_response.json')
    del mock_response['sys']['sunrise']
    
    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        with pytest.raises(OpenWeatherServiceError, match='Error parsing suntime.'):
            service.get_weather()

# Test invalid sunrise type
def test_invalid_sunrise_type(service: OpenWeatherService, base_successful_response: Callable[[str], Any]) -> None:
    mock_response = base_successful_response('openweather_success_response.json')
    mock_response['sys']['sunrise'] = 'invalid'
    
    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        with pytest.raises(OpenWeatherServiceError, match='Error parsing suntime.'):
            service.get_weather()

# Test missing sunset
def test_missing_sunset(service: OpenWeatherService, base_successful_response: Callable[[str], Any]) -> None:
    mock_response = base_successful_response('openweather_success_response.json')
    del mock_response['sys']['sunset']
    
    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        with pytest.raises(OpenWeatherServiceError, match='Error parsing suntime.'):
            service.get_weather()

# Test invalid sunset type
def test_invalid_sunset_type(service: OpenWeatherService, base_successful_response: Callable[[str], Any]) -> None:
    mock_response = base_successful_response('openweather_success_response.json')
    mock_response['sys']['sunset'] = 'invalid'
    
    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        with pytest.raises(OpenWeatherServiceError, match='Error parsing suntime.'):
            service.get_weather()

# Test missing city
def test_missing_city(service: OpenWeatherService, base_successful_response: Callable[[str], Any]) -> None:
    mock_response = base_successful_response('openweather_success_response.json')
    del mock_response['name']
    
    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        with pytest.raises(OpenWeatherServiceError):
            service.get_weather()

# Test invalid city type
def test_invalid_city_type(service: OpenWeatherService, base_successful_response: Callable[[str], Any]) -> None:
    mock_response = base_successful_response('openweather_success_response.json')
    mock_response['name'] = 12345  # Invalid type for city name
    
    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        with pytest.raises(OpenWeatherServiceError, match='Error parsing city.'):
            service.get_weather()

# Test incorrect coordinates
def test_incorrect_coordinates() -> None:
    with pytest.raises(AttributeError):
        OpenWeatherService(locator=None).get_weather()

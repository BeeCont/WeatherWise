import pytest
import json
import os
import requests
from unittest.mock import Mock, patch
from requests.exceptions import RequestException
from datetime import datetime

from exceptions.exceptions import OpenWeatherServiceError
from entities.weather import Weather, WeatherType
from entities.coordinates import Coordinates
from services.openweather_service import OpenWeatherService
from config.settings import BASE_DIR

@pytest.fixture
def service():
    locator = Coordinates(latitude=40.7128, longitude=-74.0060)
    return OpenWeatherService(locator=locator)

@pytest.fixture
def load_fixture():
    def _load_fixture(filename):
        filepath = str(BASE_DIR) + f'/fixtures/{filename}'
        with open(filepath, 'r') as file:
            return json.load(file)
    return _load_fixture
    
def test_get_weather_success(service, load_fixture):

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = load_fixture('openweather_success_response.json')

    with patch.object(requests, 'get', return_value=mock_response):

        weather = service.get_weather()
        
        
        assert isinstance(weather, Weather)
        assert weather.temperature == 23
        assert weather.weather_type == WeatherType.CLEAR
        assert weather.city == 'New York'
        assert weather.sunrise == datetime.fromtimestamp(1596242400)
        assert weather.sunset == datetime.fromtimestamp(1596292800)

def test_get_weather_error(service, load_fixture):

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = load_fixture('openweather_invalid_data_response.json')

    with patch.object(requests, 'get', return_value=mock_response):
        with pytest.raises(OpenWeatherServiceError, match=''):
            service.get_weather()

def test_get_weather_retries_on_failure(service):
    with patch.object(requests, 'get', side_effect=OpenWeatherServiceError("Error")):
        with pytest.raises(OpenWeatherServiceError):
            service.get_weather()

def test_make_request_success(service, load_fixture):

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = load_fixture('openweather_success_response.json')
    
    with patch.object(requests, 'get', return_value=mock_response):
        with patch.object(OpenWeatherService, '_check_response', return_value=mock_response.json()):
            result = service._make_request()
            expected_result = load_fixture('openweather_success_response.json')
            assert result == expected_result

def test_make_request_error(service, load_fixture):

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = load_fixture('openweather_success_response.json')

    with patch.object(OpenWeatherService, '_check_response', return_value=mock_response.json()):
        with patch.object(requests, 'get', side_effect=RequestException("Request failed")):
            with pytest.raises(OpenWeatherServiceError, match="Error while executing request"):
                service._make_request()

def test_check_response_success(service):

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {}

    with patch.object(OpenWeatherService, '_parse_json', return_value=mock_response.json()):
        with patch.object(requests, 'get', return_value=mock_response):
                result = service._check_response(mock_response)
                assert result == {}


def test_check_response_error(service):

    mock_response = Mock()
    mock_response.status_code = 500
    
    with patch.object(requests, 'get', return_value=mock_response):
        with pytest.raises(OpenWeatherServiceError, match="HTTP request error"):
            service._check_response(mock_response)

def test_parse_json_success(service, load_fixture):

    mock_response = Mock()
    mock_response.json.return_value = load_fixture('openweather_success_response.json')
    
    result = service._parse_json(mock_response)
    assert result == load_fixture('openweather_success_response.json')

def test_parse_json_error(service):

    mock_response = Mock()
    mock_response.json.side_effect = ValueError("Invalid JSON")
    
    with patch.object(requests, 'get', return_value=mock_response):
        with pytest.raises(OpenWeatherServiceError, match="JSON parsing error"):
            service._parse_json(mock_response)

def test_parse_weather_type_success(service, load_fixture):

    weather_dict = load_fixture('openweather_success_response.json')
    weather_type = service._parse_weather_type(weather_dict)
    assert weather_type == WeatherType.CLEAR

def test_parse_weather_type_error(service, load_fixture):

    weather_dict = load_fixture('openweather_invalid_data_response.json')
    with pytest.raises(OpenWeatherServiceError):
        service._parse_weather_type(weather_dict)

def test_parse_sun_time_success(service, load_fixture):

    weather_dict = load_fixture('openweather_success_response.json')
    sunrise = service._parse_sun_time(weather_dict, 'sunrise')
    sunset = service._parse_sun_time(weather_dict, 'sunset')
    
    assert sunrise == datetime.fromtimestamp(1596242400)
    assert sunset == datetime.fromtimestamp(1596292800)

def test_parse_sun_time_error(service, load_fixture):

    weather_dict = load_fixture('openweather_invalid_data_response.json')
    with pytest.raises(OpenWeatherServiceError):
        sunrise = service._parse_sun_time(weather_dict, 'sunrise')
        sunset = service._parse_sun_time(weather_dict, 'sunset')
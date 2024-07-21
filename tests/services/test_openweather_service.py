import pytest
import requests
from unittest.mock import Mock, patch
from requests.exceptions import RequestException
from datetime import datetime
from exceptions.exceptions import OpenWeatherServiceError
from entities.weather import Weather, WeatherType
from entities.coordinates import Coordinates
from services.openweather_service import OpenWeatherService

@pytest.fixture
def service():
    locator = Coordinates(latitude=40.7128, longitude=-74.0060)
    return OpenWeatherService(locator=locator)

def test_get_weather_success(service):

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'main': {'temp': 22.8},
        'weather': [{'id': 800}],
        'sys': {'sunrise': 1596242400, 'sunset': 1596292800},
        'name': 'New York'
    }

    with patch.object(requests, 'get', return_value=mock_response):

        weather = service.get_weather()
        
        
        assert isinstance(weather, Weather)
        assert weather.temperature == 23
        assert weather.weather_type == WeatherType.CLEAR
        assert weather.city == 'New York'
        assert weather.sunrise == datetime.fromtimestamp(1596242400)
        assert weather.sunset == datetime.fromtimestamp(1596292800)

def test_get_weather_retries_on_failure(service):
    with patch.object(requests, 'get', side_effect=OpenWeatherServiceError("Error")):
        with pytest.raises(OpenWeatherServiceError):
            service.get_weather()

def test_make_request_error(service):
    with patch.object(OpenWeatherService, '_check_response', return_value=Mock(status_code=200, json=lambda: {})):
        with patch.object(requests, 'get', side_effect=RequestException("Request failed")):
            with pytest.raises(OpenWeatherServiceError, match="Error while executing request"):
                service._make_request()

def test_check_response_error(service):

    mock_response = Mock()
    mock_response.status_code = 500
    
    with patch.object(requests, 'get', return_value=mock_response):
        with pytest.raises(OpenWeatherServiceError, match="HTTP request error"):
            service._check_response(mock_response)

def test_parse_json_error(service):

    mock_response = Mock()
    mock_response.json.side_effect = ValueError("Invalid JSON")
    
    with patch.object(requests, 'get', return_value=mock_response):
        with pytest.raises(OpenWeatherServiceError, match="JSON parsing error"):
            service._parse_json(mock_response)

def test_parse_weather_type(service):

    weather_dict = {'weather': [{'id': 800}]}
    weather_type = service._parse_weather_type(weather_dict)
    assert weather_type == WeatherType.CLEAR
    
    weather_dict = {'weather': [{'id': 999}]}
    with pytest.raises(OpenWeatherServiceError):
        service._parse_weather_type(weather_dict)

def test_parse_sun_time(service):

    weather_dict = {'sys': {'sunrise': 1596242400, 'sunset': 1596292800}}
    sunrise = service._parse_sun_time(weather_dict, 'sunrise')
    sunset = service._parse_sun_time(weather_dict, 'sunset')
    
    assert sunrise == datetime.fromtimestamp(1596242400)
    assert sunset == datetime.fromtimestamp(1596292800)

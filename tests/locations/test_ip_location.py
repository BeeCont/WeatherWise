import pytest
import requests
from unittest.mock import patch, Mock
from requests.exceptions import RequestException

from locations.ip_location import IPLocator
from entities.coordinates import Coordinates
from exceptions.exceptions import IPLocatorError

@pytest.fixture
def ip_locator():
    return IPLocator("http://example.com")

def test_get_coordinates_success(ip_locator):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'lat': '12.34', 'lon': '56.78'}

    with patch.object(requests, 'get', return_value=mock_response):
        coordinates = ip_locator.get_coordinates()
        assert coordinates.latitude == 12.34
        assert coordinates.longitude == 56.78

def test_get_coordinates_request_exception(ip_locator):
    with patch.object(requests, 'get', side_effect=RequestException("Network error")):
        with pytest.raises(IPLocatorError, match="Error while executing request"):
            ip_locator.get_coordinates()

def test_get_coordinates_http_error(ip_locator):
    mock_response = Mock()
    mock_response.status_code = 404

    with patch.object(requests, 'get', return_value=mock_response):
        with pytest.raises(IPLocatorError, match="HTTP request error. Status code"):
            ip_locator.get_coordinates()

def test_get_coordinates_json_parsing_error(ip_locator):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")

    with patch.object(requests, 'get', return_value=mock_response):
        with pytest.raises(IPLocatorError, match="JSON parsing error"):
            ip_locator.get_coordinates()

def test_get_coordinates_key_error(ip_locator):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'longitude': '56.78'}  # Missing 'lat' key

    with patch.object(requests, 'get', return_value=mock_response):
        with pytest.raises(IPLocatorError, match="Error parsing coordinates"):
            ip_locator.get_coordinates()

def test_get_coordinates_value_error(ip_locator):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'lat': 'invalid', 'lon': '56.78'}  # 'lat' is not a float

    with patch.object(requests, 'get', return_value=mock_response):
        with pytest.raises(IPLocatorError, match="Error parsing coordinates"):
            ip_locator.get_coordinates()

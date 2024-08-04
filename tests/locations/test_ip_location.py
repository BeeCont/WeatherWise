import pytest
from unittest.mock import MagicMock, patch
from requests.exceptions import RequestException
from entities.coordinates import Coordinates
from exceptions.exceptions import IPLocatorError
from locations.ip_location import IPLocator

@pytest.fixture
def ip_locator() -> IPLocator:
    # Provide a test IPLocator instance
    return IPLocator(ip_url="http://example.com")

def test_successful_get_coordinates(ip_locator: IPLocator) -> None:
    # Test valid coordinate extraction
    mock_response = {'lat': 40.7128, 'lon': -74.0060}
    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        coordinates = ip_locator.get_coordinates()
        assert coordinates == Coordinates(latitude=40.7128, longitude=-74.0060)

def test_request_exception(ip_locator: IPLocator) -> None:
    # Test handling of a RequestException
    with patch('requests.get', side_effect=RequestException):
        with pytest.raises(IPLocatorError, match='Error while executing request'):
            ip_locator.get_coordinates()

def test_http_error_status_code(ip_locator: IPLocator) -> None:
    # Test handling of HTTP error status code 404
    with patch('requests.get', return_value=MagicMock(status_code=404)):
        with pytest.raises(IPLocatorError, match='HTTP request error. Status code: 404'):
            ip_locator.get_coordinates()

def test_json_parsing_error(ip_locator: IPLocator) -> None:
    # Test handling of JSON parsing error
    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(side_effect=ValueError))):
        with pytest.raises(IPLocatorError, match='JSON parsing error'):
            ip_locator.get_coordinates()

def test_missing_latitude_key(ip_locator: IPLocator) -> None:
    # Test missing latitude key in response
    mock_response = {'lon': -74.0060}
    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        with pytest.raises(IPLocatorError, match='Error parsing coordinates'):
            ip_locator.get_coordinates()

def test_missing_longitude_key(ip_locator: IPLocator) -> None:
    # Test missing longitude key in response
    mock_response = {'lat': 40.7128}
    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        with pytest.raises(IPLocatorError, match='Error parsing coordinates'):
            ip_locator.get_coordinates()

def test_invalid_latitude_value(ip_locator: IPLocator) -> None:
    # Test invalid latitude value
    mock_response = {'lat': 'invalid', 'lon': -74.0060}
    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        with pytest.raises(IPLocatorError, match='Error parsing coordinates'):
            ip_locator.get_coordinates()

def test_invalid_longitude_value(ip_locator: IPLocator) -> None:
    # Test invalid longitude value
    mock_response = {'lat': 40.7128, 'lon': 'invalid'}
    with patch('requests.get', return_value=MagicMock(status_code=200, json=MagicMock(return_value=mock_response))):
        with pytest.raises(IPLocatorError, match='Error parsing coordinates'):
            ip_locator.get_coordinates()
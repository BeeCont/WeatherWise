"""
Unit tests for the IPLocator service.

This module verifies the behavior of the `IPLocator` class when retrieving
geographical coordinates by IP address. Tests cover both successful
responses and various failure scenarios introduced by the new exception
handling system.

Covered scenarios:
- Successful extraction of latitude and longitude.
- Network-level failures during HTTP requests.
- Handling of non-200 HTTP status codes.
- JSON parsing errors in API responses.
- Domain-level validation errors for missing or invalid coordinates.

The tests ensure that:
- All low-level errors are wrapped into `InfrastructureError`.
- Domain validation issues raise `InvalidCoordinatesError`.
- The public service interface consistently raises `IPLocatorError`
  with proper exception chaining via `__cause__`.

External dependencies such as HTTP requests are mocked to guarantee
deterministic and isolated test behavior.
"""

import pytest
from unittest.mock import MagicMock, patch
from requests.exceptions import RequestException

from entities.coordinates import Coordinates
from exceptions.locator_exceptions import IPLocatorError
from exceptions.infrastructure_exceptions import (
    InfrastructureError, HttpRequestError, JsonParseError
)
from exceptions.domain_exceptions import InvalidCoordinatesError
from locations.ip_location import IPLocator


@pytest.fixture
def ip_locator() -> IPLocator:
    """
    Provide a test IPLocator instance with a dummy URL.

    Returns:
        IPLocator: An instance of the IPLocator service.
    """
    return IPLocator(ip_url="http://example.com")

EXPECTED_LOCATOR_ERROR = "Failed to get coordinates from IP location service."

def test_successful_get_coordinates(ip_locator: IPLocator) -> None:
    """
    Verify successful coordinate extraction from a valid API response.

    Ensures that the service correctly parses latitude and longitude.
    """
    mock_response = {'lat': 40.7128, 'lon': -74.0060}

    with patch('requests.get', return_value=MagicMock(
        status_code=200,
        json=MagicMock(return_value=mock_response)
    )):
        coordinates = ip_locator.get_coordinates()
        assert coordinates == Coordinates(latitude=40.7128, longitude=-74.0060)


def test_request_exception(ip_locator: IPLocator) -> None:
    """
    Simulate a network failure and check wrapping into InfrastructureError.

    The public interface should raise IPLocatorError with __cause__ set.
    """
    with patch('requests.get', side_effect=RequestException):
        with pytest.raises(IPLocatorError) as exc_info:
            ip_locator.get_coordinates()

        assert exc_info.value.message == EXPECTED_LOCATOR_ERROR
        cause = exc_info.value.__cause__
        assert isinstance(cause, InfrastructureError)
        assert "Error during IP location request." in cause.message


def test_http_error_status_code(ip_locator: IPLocator) -> None:
    """
    Simulate an HTTP error (404) and check proper exception chaining.

    InfrastructureError wraps HttpRequestError and is exposed via IPLocatorError.
    """
    with patch('requests.get', return_value=MagicMock(status_code=404)):
        with pytest.raises(IPLocatorError) as exc_info:
            ip_locator.get_coordinates()

        assert exc_info.value.message == EXPECTED_LOCATOR_ERROR
        infra_cause = exc_info.value.__cause__
        assert isinstance(infra_cause, InfrastructureError)
        http_cause = infra_cause.__cause__
        assert isinstance(http_cause, HttpRequestError)
        assert http_cause.http_status == 404


def test_json_parsing_error(ip_locator: IPLocator) -> None:
    """
    Simulate JSON parsing error and check proper exception chaining.

    InfrastructureError wraps JsonParseError and is exposed via IPLocatorError.
    """
    with patch('requests.get', return_value=MagicMock(
        status_code=200,
        json=MagicMock(side_effect=ValueError)
    )):
        with pytest.raises(IPLocatorError) as exc_info:
            ip_locator.get_coordinates()

        assert exc_info.value.message == EXPECTED_LOCATOR_ERROR
        infra_cause = exc_info.value.__cause__
        assert isinstance(infra_cause, InfrastructureError)
        json_cause = infra_cause.__cause__
        assert isinstance(json_cause, JsonParseError)


def test_missing_latitude_key(ip_locator: IPLocator) -> None:
    """
    Verify handling when latitude is missing in the API response.

    Should raise InvalidCoordinatesError wrapped in IPLocatorError.
    """
    mock_response = {'lon': -74.0060}

    with patch('requests.get', return_value=MagicMock(
        status_code=200,
        json=MagicMock(return_value=mock_response)
    )):
        with pytest.raises(IPLocatorError) as exc_info:
            ip_locator.get_coordinates()

        pars_cause = exc_info.value.__cause__
        assert isinstance(pars_cause, InvalidCoordinatesError)
        assert "Error parsing coordinates" in pars_cause.message


def test_missing_longitude_key(ip_locator: IPLocator) -> None:
    """
    Verify handling when longitude is missing in the API response.

    Should raise InvalidCoordinatesError wrapped in IPLocatorError.
    """
    mock_response = {'lat': 40.7128}

    with patch('requests.get', return_value=MagicMock(
        status_code=200,
        json=MagicMock(return_value=mock_response)
    )):
        with pytest.raises(IPLocatorError) as exc_info:
            ip_locator.get_coordinates()
        
        pars_cause = exc_info.value.__cause__
        assert isinstance(pars_cause, InvalidCoordinatesError)
        assert "Error parsing coordinates" in pars_cause.message


def test_invalid_latitude_value(ip_locator: IPLocator) -> None:
    """
    Verify handling when latitude value is invalid (non-numeric).

    Should raise InvalidCoordinatesError wrapped in IPLocatorError.
    """
    mock_response = {'lat': 'invalid', 'lon': -74.0060}

    with patch('requests.get', return_value=MagicMock(
        status_code=200,
        json=MagicMock(return_value=mock_response)
    )):
        with pytest.raises(IPLocatorError) as exc_info:
            ip_locator.get_coordinates()

        pars_cause = exc_info.value.__cause__
        assert isinstance(pars_cause, InvalidCoordinatesError)
        assert "Error parsing coordinates" in pars_cause.message


def test_invalid_longitude_value(ip_locator: IPLocator) -> None:
    """
    Verify handling when longitude value is invalid (non-numeric).

    Should raise InvalidCoordinatesError wrapped in IPLocatorError.
    """
    mock_response = {'lat': 40.7128, 'lon': 'invalid'}

    with patch('requests.get', return_value=MagicMock(
        status_code=200,
        json=MagicMock(return_value=mock_response)
    )):
        with pytest.raises(IPLocatorError) as exc_info:
            ip_locator.get_coordinates()
        
        pars_cause = exc_info.value.__cause__
        assert isinstance(pars_cause, InvalidCoordinatesError)
        assert "Error parsing coordinates" in pars_cause.message
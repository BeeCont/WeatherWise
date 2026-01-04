"""
Unit tests for the HttpJsonMixin.

This module tests the core functionality of the `HttpJsonMixin`, which provides
methods for performing HTTP GET requests and parsing JSON responses. The tests
ensure that:

- Successful HTTP requests return the expected JSON.
- Network errors are correctly wrapped in `InfrastructureError`.
- Non-200 HTTP status codes raise `HttpRequestError`.
- Malformed JSON raises `JsonParseError`.

The mixin is tested in isolation using a dummy class that inherits from it,
with all external HTTP requests mocked to ensure deterministic behavior.
"""

import pytest
from unittest.mock import MagicMock, patch
from requests.exceptions import RequestException

from mixins.http_json_mixin import HttpJsonMixin
from exceptions.infrastructure_exceptions import (
    InfrastructureError, HttpRequestError, JsonParseError
)


class TestHttpJsonMixin(HttpJsonMixin):
    """Dummy test class inheriting HttpJsonMixin for isolated testing."""
    pass


@pytest.fixture
def http_json_mixin() -> TestHttpJsonMixin:
    """
    Provides a fresh instance of the test mixin class for each test.

    Returns:
        TestHttpJsonMixin: An instance of the dummy test class.
    """
    return TestHttpJsonMixin()


def test_make_http_request_success(http_json_mixin) -> None:
    """
    Test that `_make_http_request` successfully performs an HTTP GET request 
    and returns parsed JSON data.

    The test mocks `requests.get` to return a valid response with JSON.
    """
    mock_response = MagicMock(status_code=200)
    mock_response.json.return_value = {'key': 'value'}

    with patch('requests.get', return_value=mock_response):
        result = http_json_mixin._make_http_request('https://example.com/api')
        assert result == {'key': 'value'}


def test_make_http_request_failure(http_json_mixin) -> None:
    """
    Test that `_make_http_request` correctly wraps network errors.

    When a `RequestException` occurs, the method should raise
    `InfrastructureError` with an appropriate message.
    """
    with patch('requests.get', side_effect=RequestException):
        with pytest.raises(InfrastructureError) as exc_info:
            http_json_mixin._make_http_request('https://example.com/api')

        assert "Error during HTTP API request." in str(exc_info.value)


def test_check_http_response_status_no_200(http_json_mixin):
    """
    Test that `_check_http_response` raises `HttpRequestError` for non-200
    HTTP status codes.

    The raised exception should include the actual HTTP status code and a
    descriptive message.
    """
    mock_response = MagicMock(status_code=404)

    with pytest.raises(HttpRequestError) as exc_info:
        http_json_mixin._check_http_response(mock_response)

    assert exc_info.value.http_status == 404
    assert "Failed to retrieve valid data from the API." in exc_info.value.message


def test_parse_json_response_invalid(http_json_mixin):
    """
    Test that `_parse_json_response` raises `JsonParseError` for invalid JSON.

    The test simulates a response where `response.json()` raises `ValueError`.
    """
    mock_response = MagicMock(status_code=200)
    mock_response.json.side_effect = ValueError

    with pytest.raises(JsonParseError) as exc_info:
        http_json_mixin._parse_json_response(mock_response)

    assert "Failed to parse JSON response from API." in exc_info.value.message
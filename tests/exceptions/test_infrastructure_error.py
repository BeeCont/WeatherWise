"""
Unit tests for the InfrastructureError class.

This module tests how the InfrastructureError exception behaves in different
situations. The goal is to make sure the error is created correctly and that
its message is formatted in a clear and predictable way.

The tests check:
- Default values of inherited and custom fields.
- Custom initialization with user-defined parameters.
- Correct formatting of messages, including the http_status field.
- Behavior when http_status is not provided and default values are used.

These tests help ensure that infrastructure-related errors are reliable
and easy to debug.
"""

from datetime import datetime

import pytest
from freezegun import freeze_time

from exceptions.base_exception import ErrorSeverity, ErrorLayer
from exceptions.infrastructure_exceptions import InfrastructureError


@freeze_time("2025-01-01 12:00:00")
def test_infrastructure_error_defaults():
    """Test creating an InfrastructureError with default parameters.

    This test verifies that all attributes (inherited and specific) are correctly set
    to their default values when no parameters are provided, including the subclass-specific
    http_status.
    """
    err = InfrastructureError()

    # Inherited defaults from AppError (quick check)
    assert err.message == "An infrastructure error occurred."  # Subclass default
    assert err.severity == ErrorSeverity.ERROR
    assert isinstance(err.severity, ErrorSeverity)  # Type
    assert err.code == ErrorLayer.NETWORK_ERROR  # Subclass default
    assert isinstance(err.code, ErrorLayer)  # Type
    assert err.details is None

    # Subclass-specific (http_status)
    assert err.http_status == 500  # Default

    # Dynamic field (created_at)
    assert err.created_at is not None
    assert isinstance(err.created_at, datetime)
    assert err.created_at == datetime(2025, 1, 1, 12, 0, 0)

@freeze_time("2025-01-01 12:00:00")
def test_infrastructure_error_custom_init():
    """Test creating an InfrastructureError with custom initialization parameters.

    This test verifies that all attributes (inherited and specific) are correctly set
    when custom parameters are provided, including the subclass-specific http_status.
    """
    custom_message = "Custom infrastructure error"
    custom_severity = ErrorSeverity.CRITICAL
    custom_code = ErrorLayer.PARSE_ERROR
    custom_http_status = 503
    custom_details = {"service": "external_api"}

    err = InfrastructureError(
        message=custom_message,
        severity=custom_severity,
        code=custom_code,
        http_status=custom_http_status,
        details=custom_details
    )

    # Inherited attributes from AppError
    assert err.message == custom_message
    assert err.severity == custom_severity
    assert err.code == custom_code
    assert err.details == custom_details

    # Subclass-specific (http_status)
    assert err.http_status == custom_http_status

    # Dynamic field (created_at)
    assert err.created_at is not None
    assert isinstance(err.created_at, datetime)
    assert err.created_at == datetime(2025, 1, 1, 12, 0, 0)

def test_infrastructure_error_format_message_with_http_status():
    """Test the formatted message of InfrastructureError includes http_status.

    This test verifies that the string representation of the error correctly
    formats the message to include the http_status attribute.
    """
    custom_http_status = 504

    err = InfrastructureError(
        http_status=custom_http_status
    )

    formatted_message = err.format_message()

    assert f" | http_status={custom_http_status}" in formatted_message

def test_infrastructure_error_format_message_without_http_status():
    """Test the formatted message of InfrastructureError with default http_status.

    This test verifies that the string representation of the error correctly
    formats the message to include the default http_status when none is provided.
    """
    # Case 1: details is None
    err_none = InfrastructureError(message="Error with no http_status", http_status=None)
    output_none = err_none.format_message()
    assert " | http_status =" in output_none

    # Case 2: details is an empty dictionary
    err_empty = InfrastructureError(message="Error with empty http_status", details={})
    output_empty = err_empty.format_message()
    assert " | http_status =" in output_empty
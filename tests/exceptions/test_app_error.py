"""
Unit tests for the AppError class and its related enums.

This module checks how AppError works in different situations. It tests
default values, custom arguments, string formatting, and exception chaining.
The goal is to make sure the error class behaves correctly and always
produces a clear and consistent message.

The tests cover:
- Creating errors with default and custom settings.
- Message formatting (timestamp, code, severity, details).
- Chaining errors using 'cause' with both custom and built-in exceptions.
- Edge cases such as missing or empty values.
"""

from datetime import datetime

import pytest
from freezegun import freeze_time

from exceptions.base_exceptions import AppError, ErrorSeverity, ErrorLayer


@freeze_time("2025-01-01 12:00:00")
def test_app_error_without_parameters():
    """Test creating an AppError with default parameters.

    This test verifies that all atributes are set to their default values 
    when no parameters are provided.
    """
    err = AppError()

    # Defaults checks (static fields)    
    assert err.message == "An application error occurred."
    assert isinstance(err.severity, ErrorSeverity)
    assert isinstance(err.code, ErrorLayer)
    assert err.details is None

    # Created_at checks (dynamic field)
    assert err.created_at is not None
    assert isinstance(err.created_at, datetime)
    assert err.created_at == datetime(2025, 1, 1, 12, 0, 0)

def test_app_error_with_custom_init():
    """Test creating an AppError with custom initialization parameters.

    This test verifies that all atributes are correctly set when
    custom parameters are provided.
    """
    custom_message = "Custom error message"
    custom_severity = ErrorSeverity.WARNING
    custom_code = ErrorLayer.VALIDATION_ERROR
    custom_details = {"field": "value"}

    err = AppError(
        message=custom_message,
        severity=custom_severity,
        code=custom_code,
        details=custom_details
    )

    # Custom parameters checks (static fields)   
    assert err.message == custom_message
    assert err.severity == custom_severity
    assert err.code == custom_code
    assert err.details == custom_details

    # Created_at checks (dynamic field)
    assert err.created_at is not None
    assert isinstance(err.created_at, datetime)

@freeze_time("2025-01-01 12:00:00")
def test_app_error_format_message_with_details():
    """Test the format_message method of AppError.

    This test verifies that the formatted message includes all relevant
    information in the expected format.
    """
    custom_message = "Custom error message"
    custom_severity = ErrorSeverity.ERROR
    custom_code = ErrorLayer.VALIDATION_ERROR
    custom_details = {"tempreature": "invalid temperture value"}

    err = AppError(
        message=custom_message,
        severity=custom_severity,
        code=custom_code,
        details=custom_details
    )

    output_message = err.format_message()

    # Check that all components are in the formatted message
    assert "2025-01-01 12:00:00" in output_message
    assert "[VALIDATION_ERROR]" in output_message
    assert "[ERROR]" in output_message
    assert custom_message in output_message
    assert f" | details = {custom_details}" in output_message

def test_app_error_format_message_without_details():
    """Test the format_message method when details are empty or None.

    This test verifies that the formatted message does not include
    the details section when details are not provided or empty.
    """
    # Case 1: details is None
    err_none = AppError(message="Error with no details", details=None)
    output_none = err_none.format_message()
    assert " | details =" not in output_none

    # Case 2: details is an empty dictionary
    err_empty = AppError(message="Error with empty details", details={})
    output_empty = err_empty.format_message()
    assert " | details =" not in output_empty

def test_app_error_chaining_with_builtin_exception():
    """Test that AppError correctly chains the original exception.

    This test verifies that the original exception is preserved
    when using "raise ... from ...".
    """
    # Case 1: Chaining with built-in exception
    original_exception = ValueError("Original error")

    try:
        raise AppError("Chained error") from original_exception
    except AppError as err:
        # Check that the cause is the original exception
        assert err.__cause__ is original_exception
        assert isinstance(err.__cause__, ValueError)
        assert str(err.__cause__) == "Original error"
        assert err.message == "Chained error"
        assert f"Caused by: {repr(original_exception)}" in err.format_message()

def test_app_error_multi_level_chaining():
    """Test multi-level exception chaining with AppError.

    This test verifies that multiple levels of exception chaining
    are preserved and correctly represented in the formatted message.
    """
    # Case 2: Multi-level chaining with another AppError
    inner_cause = ValueError("Innermost error")
    mid_err = AppError("Middle error")
    mid_err.__cause__ = inner_cause
    output_err = AppError("Outer error")

    try:
        raise output_err from mid_err
    except AppError as err:
        # Check that the cause is the middle AppError
        assert err.__cause__ is mid_err
        assert isinstance(err.__cause__, AppError)
        assert err.__cause__.message == "Middle error"
        # Check that the inner cause is preserved
        mid_cause = err.__cause__.__cause__
        assert mid_cause is inner_cause
        assert isinstance(mid_cause, ValueError)
        assert str(mid_cause) == "Innermost error"
        # Check formatted message includes both causes
        formatted_message = err.format_message()
        assert "Caused by: " in formatted_message
        assert "Middle error" in formatted_message
        assert "Innermost error" in formatted_message

@freeze_time("2025-01-01 12:00:00")
def test_app_error_edge_cases():
    """Test edge cases for AppError initialization and formatting.

    This test verifies behavior with None or empty parameters, ensuring
    defaults are applied correctly and no unexpected output is generated.
    """
    # None message and empty details
    err = AppError(message=None, details={})
    assert err.message == "An application error occurred."  # Default applied
    output = str(err)
    assert "details" not in output  # No details line if empty dict

    # All None parameters
    err_all_none = AppError(message=None, severity=None, code=None, details=None)
    assert err_all_none.severity == ErrorSeverity.ERROR  # Default
    assert err_all_none.code == ErrorLayer.APP_ERROR  # Default
    assert "details" not in str(err_all_none)  # No line
    assert err_all_none.created_at == datetime(2025, 1, 1, 12, 0, 0)  # Mocked time
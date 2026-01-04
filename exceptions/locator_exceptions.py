from .infrastructure_exceptions import InfrastructureError

class BaseLocatorError(InfrastructureError):
    default_message = "An error occurred in the locator service."
    default_http_status = 502  # Bad Gateway

class IPLocatorError(InfrastructureError):
    default_message = "Failed to get coordinates from IPLocator service."

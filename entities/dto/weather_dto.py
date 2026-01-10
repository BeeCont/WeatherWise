from datetime import datetime
from pydantic import BaseModel


class WeatherDTO(BaseModel):
    """A Data Transfer Object (DTO) for conveying weather information.

    This model encapsulates various weather details received from an API,
    such as temperature, humidity, wind speed, and other related metrics.
    Detailed information for each field is provided inline.
    
    Some fields are optional to support incomplete data returned by
    external weather services.

    The current set of required fields reflects the needs of existing
    services. In future iterations, additional fields may become
    optional as new services are added or data availability changes.
    """
    city_name: str # City name
    temp: float # Current temperature (°C)
    feels_like: int # Feels-like temperature (°C)
    temp_min: int # Minimum temperature (°C)
    temp_max: int # Maximum temperature (°C)
    pressure: int # Atmospheric pressure (hPa)
    humidity: int # Humidity percentage
    wind_speed: float | None = None # Wind speed (m/s)
    wind_dir: str | None = None # Wind direction (e.g., N, NE, SW)
    visibility_km: float | None = None # Visibility in kilometers
    clouds: int | None = None # Cloudiness percentage
    sunrise: datetime | None = None # Sunrise time
    sunset: datetime | None = None # Sunset time
    description: str # Weather description

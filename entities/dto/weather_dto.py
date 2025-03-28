from datetime import datetime
from pydantic import BaseModel, Field


class WeatherDTO(BaseModel):
    """A Data Transfer Object (DTO) for conveying weather information.

    This model encapsulates various weather details received from an API,
    such as temperature, humidity, wind speed, and other related metrics.
    Detailed information for each field is provided inline.
    """
    city_name: str # City name
    temp: float # Current temperature (°C)
    feels_like: int # Feels-like temperature (°C)
    temp_min: int # Minimum temperature (°C)
    temp_max: int # Maximum temperature (°C)
    pressure: int # Atmospheric pressure (hPa)
    humidity: int # Humidity percentage
    wind_speed: float # Wind speed (m/s)
    wind_dir: str # Wind direction (e.g., N, NE, SW)
    visibility_km: float # Visibility in kilometers
    clouds: int # Cloudiness percentage
    sunrise: datetime # Sunrise time
    sunset: datetime # Sunset time
    description: str # Weather description

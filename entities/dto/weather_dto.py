from pydantic import BaseModel
from datetime import datetime


class WeatherDTO(BaseModel):
    city_name: str
    temp: float
    feels_like: int
    temp_min: int
    temp_max: int
    pressure: int
    humidity: int
    wind_speed: float
    wind_dir: str
    visibility_km: float
    clouds: int
    sunrise: datetime
    sunset: datetime
    description: str

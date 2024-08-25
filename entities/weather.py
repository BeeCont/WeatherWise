from typing import TypeAlias
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class WeatherType(str, Enum):
    THUNDERSTORM = "Thunderstorm"
    DRIZZLE = "Drizzle"
    RAIN = "Rain"
    SNOW = "Snow"
    CLEAR = "Clear"
    FOG = "Fog"
    CLOUDS = "Clouds"

@dataclass(slots=True, frozen=True)
class Weather:
    temperature: float
    temperature_feels_like: float
    temperature_min: float
    temperature_max: float
    pressure: int
    weather_type: WeatherType
    wind_speed: float
    wind_dir: str
    visibility: float
    clouds: int
    humidity: int
    description: str
    sunrise: datetime
    sunset: datetime
    city: str
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
    weather_type: WeatherType
    sunrise: datetime
    sunset: datetime
    city: str
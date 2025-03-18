from pydantic import BaseModel, Field
from typing import List


class SysData(BaseModel):
    sunrise: int = Field(..., ge=0)  # Time must be positive
    sunset: int = Field(..., ge=0)


class CloudData(BaseModel):
    all: int = Field(..., ge=0, le=100)  # Clouds in % (0-100)


class WindData(BaseModel):
    speed: float = Field(..., ge=0)  # Wind speed must be 0 or more
    deg: int = Field(..., ge=0, le=360)  # Wind direction (0-360°)


class MainWeatherData(BaseModel):
    temp: float = Field(..., ge=-100, le=100)  # Temperature (-100 to 100°C)
    feels_like: float = Field(..., ge=-100, le=100)
    temp_min: float = Field(..., ge=-100, le=100)
    temp_max: float = Field(..., ge=-100, le=100)
    pressure: int = Field(..., gt=0)  # Pressure must be positive
    humidity: float = Field(..., ge=0, le=100)  # Humidity (0-100%)


class WeatherCondition(BaseModel):
    id: int = Field(..., ge=0) # ID must be 0 or more
    description: str


class OpenWeatherSchema(BaseModel):
    main: MainWeatherData
    weather: List[WeatherCondition]
    wind: WindData
    visibility: int = Field(..., ge=0)  # Visibility must be 0 or more
    clouds: CloudData
    sys: SysData
    name: str

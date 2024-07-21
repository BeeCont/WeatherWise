import environ

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(env_file=str(BASE_DIR) + '/env/.env')

#IP settings
IP_URL = 'http://ip-api.com/json/'

#OpenWeather settings
OPENWEATHER_API = env('OPENWEATHER_API')
OPENWEATHER_URL_TEMPLATE = (
    "https://api.openweathermap.org/data/2.5/weather?"
    "lat={latitude}&lon={longitude}&"
    "appid=" + OPENWEATHER_API + "&lang=en&"
    "units=metric"
)
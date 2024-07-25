# WeatherWise

## Description

This repository has a small Python program to get the current weather. The program uses weather API services to get data and show information about the current temperature and weather conditions for a given location.

## Features

- **API Integration**: Uses public APIs to get weather data.
- **Geolocation**: Finds the user's location automatically (optional) or by given address.
- **User-Friendly Interface**: Simple command-line interface or GUI to show the weather information.
- **Configuration Files**: Set API keys and other settings through config files.
- **Modular Structure**: Split into modules for API work, data processing, and showing results.


## Repository Structure
```
WeatherWise/
├── COMMIT_CONVENTIONS.md
├── config
│   └── settings.py
├── entities
│   ├── coordinates.py
│   └── weather.py
├── env
├── exceptions
│   └── exceptions.py
├── formatters
│   └── console_weather_formatter.py
├── locations
│   ├── base_location.py
│   └── ip_location.py
├── README.md
├── requirements.txt
├── services
│   └── openweather_service.py
├── tests
│   ├── __init__.py
│   └── locations
└── weather
```

## Usage Instructions

1. Install the dependencies listed in requirements.txt.
1. Set up the settings file `env/.env` using `env/.env_example` as a template.
2. Run weather to get the current weather for your location or a given address.

## Contributing

This project follows the principles of writing comments described [in this documentation](COMMIT_CONVENTIONS.md ).
#
This project is made as a learning app to show how to work with APIs and data in Python.
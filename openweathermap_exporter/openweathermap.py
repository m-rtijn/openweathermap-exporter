from datetime import datetime
from functools import lru_cache
import json
from typing import Optional
import requests

GEOCODING_API_BASE_URL="http://api.openweathermap.org/geo/1.0/direct"
CURRENT_WEATHER_API_BASE_URL="https://api.openweathermap.org/data/2.5/weather"
CURRENT_AIR_POLLUTION_API_BASE_URL="http://api.openweathermap.org/data/2.5/air_pollution"

class Coordinate:

    lat: float
    lon: float

    def __init__(self, **kwargs):
        try:
            self.lat = kwargs["lat"]
            self.lon = kwargs["lon"]
        except KeyError:
            self.lat = kwargs["obj"]["lat"]
            self.lon = kwargs["obj"]["lon"]
    
    def __str__(self):
        return f"Coordinate(lat={self.lat}, lon={self.lon})"

class WeatherInformation:
    coord: Coordinate

    # TODO: Maybe add weather condition parsing?

    temp: float
    temp_feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int
    visibility: int
    wind_speed: float
    wind_deg: float
    wind_gust: Optional[float]
    cloudiness: float
    rain_volume_1h: Optional[float]
    rain_volume_3h: Optional[float]

    # TODO: Add parsing for snow

    timestamp: datetime
    sunrise: datetime
    sunset: datetime

    def __init__(self, obj: dict):
        """Create WeatherInformation object from a dictionary result from the CurrentWeather API"""
        self.coord = Coordinate(obj=obj["coord"])
        self.temp = obj["main"]["temp"]
        self.temp_feels_like = obj["main"]["feels_like"]
        self.temp_max = obj["main"]["temp_max"]
        self.temp_min = obj["main"]["temp_min"]
        self.pressure = obj["main"]["pressure"]
        self.humidity = obj["main"]["humidity"]
        self.visibility = obj["visibility"]
        self.wind_deg = obj["wind"]["deg"]
        try:
            self.wind_gust = obj["wind"]["gust"]
        except KeyError:
            self.wind_gust = None
        self.wind_speed = obj["wind"]["speed"]
        self.cloudiness = obj["clouds"]["all"]
        try:
            self.rain_volume_1h = obj["rain"]["1h"]
        except KeyError:
            self.rain_volume_1h = None
        try:
            self.rain_volume_3h = obj["rain"]["3h"]
        except KeyError:
            self.rain_volume_3h = None
        self.timestamp = datetime.fromtimestamp(obj["dt"])
        self.sunrise = datetime.fromtimestamp(obj["sys"]["sunrise"])
        self.sunset = datetime.fromtimestamp(obj["sys"]["sunset"])

    def __str__(self):
        return f"WeatherInformation(temp={self.temp}, humidity={self.humidity}, timestamp={self.timestamp}, coord={self.coord})"

class OpenWeatherMap:

    api_key: str

    def __init__(self, api_key: str):
        self.api_key = api_key

    def owm_api_request(self, base_url: str, parameters: dict, timeout_time=10) -> dict:
        """Do a request to an OpenWeatherMap API endpoint."""

        parameters["appid"] = self.api_key

        resp = requests.get(base_url, params=parameters, timeout=timeout_time)

        return json.loads(resp.text)

    @lru_cache(maxsize=64)
    def get_coordinate(self, location_name: str, country_code: str) -> Coordinate:
        """Use Geocoding API to map a location_name and country_code to a coordinate.

        https://openweathermap.org/api/geocoding-api
        """

        parameters = {"q" : f"{location_name},{country_code}", "limit": 1}

        resp = self.owm_api_request(GEOCODING_API_BASE_URL, parameters)[0]

        return Coordinate(obj=resp)

    def get_current_weather(self, coord: Coordinate, units="metric") -> WeatherInformation:
        """Use Current Weather API to get current weather information

        https://openweathermap.org/current
        """

        parameters = {"lat": coord.lat, "lon": coord.lon, "units": units}

        resp = self.owm_api_request(CURRENT_WEATHER_API_BASE_URL, parameters)

        return WeatherInformation(resp)

class Location:

    location_name: str
    country_code: str

    coord: Coordinate

    def __init__(self, location_name: str, country_code: str, owm: OpenWeatherMap):
        self.location_name = location_name
        self.country_code = country_code
        self.coord = owm.get_coordinate(location_name, country_code)
    
    def get_weather(self, owm: OpenWeatherMap) -> WeatherInformation:
        return owm.get_current_weather(self.coord)

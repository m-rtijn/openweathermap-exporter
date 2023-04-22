"""
    openweathermap.py

    Copyright (c) 2023 Martijn <martijn [at] mrtijn.nl>

    https://github.com/m-rtijn/openweathermap-exporter

    This file is part of openweathermap-exporter.

    openweathermap-exporter is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    openweathermap-exporter is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with openweathermap-exporter. If not, see <https://www.gnu.org/licenses/>.

    SPDX-License-Identifier: AGPL-3.0-or-later
"""


from datetime import datetime, timedelta
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
    snow_volume_1h: Optional[float]
    snow_volume_3h: Optional[float]
    timestamp: datetime
    sunrise: datetime
    sunset: datetime

    def __init__(self, obj: dict):
        """Create WeatherInformation object from a dictionary result from the OWM CurrentWeather API

        https://openweathermap.org/current
        """
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
        try:
            self.snow_volume_1h = obj["snow"]["1h"]
        except KeyError:
            self.snow_volume_1h = None
        try:
            self.snow_volume_3h = obj["snow"]["3h"]
        except KeyError:
            self.snow_volume_3h = None
        self.timestamp = datetime.fromtimestamp(obj["dt"])
        self.sunrise = datetime.fromtimestamp(obj["sys"]["sunrise"])
        self.sunset = datetime.fromtimestamp(obj["sys"]["sunset"])

    def __str__(self):
        return f"WeatherInformation(temp={self.temp}, humidity={self.humidity}, timestamp={self.timestamp}, coord={self.coord})"

class AirPollutionInformation:
    coord: Coordinate
    timestamp: datetime
    air_quality_index: int
    co: float
    no: float
    no2: float
    o3: float
    so2: float
    pm2_5: float
    pm10: float
    nh3: float

    def __init__(self, obj: dict):
        """Parse air pollution information from the OWM Air Pollution API.

        https://openweathermap.org/api/air-pollution
        """

        self.coord = Coordinate(obj=obj["coord"])
        res_obj = obj["list"][0]
        self.timestamp = datetime.fromtimestamp(res_obj["dt"])
        self.air_quality_index = res_obj["main"]["aqi"]
        self.co = res_obj["components"]["co"]
        self.no = res_obj["components"]["no"]
        self.no2 = res_obj["components"]["no2"]
        self.o3 = res_obj["components"]["o3"]
        self.so2 = res_obj["components"]["so2"]
        self.pm2_5 = res_obj["components"]["pm2_5"]
        self.pm10 = res_obj["components"]["pm10"]
        self.nh3 = res_obj["components"]["nh3"]

    def __str__(self):
        return f"""AirPollutionInformation(timestamp={self.timestamp}, aqi={self.air_quality_index}, co={self.co},
            no={self.no}, no2={self.no2}, o3={self.o3}, so2={self.so2}, pm2_5={self.pm2_5},
            pm10={self.pm10}, nh3={self.nh3})"""

class OpenWeatherMap:

    api_key: str

    def __init__(self, api_key: str):
        self.api_key = api_key

    # TODO: Add request self-limiting
    def owm_api_request(self, base_url: str, parameters: dict, timeout_time=10) -> dict:
        """Do a request to an OpenWeatherMap API endpoint."""

        parameters["appid"] = self.api_key

        resp = requests.get(base_url, params=parameters, timeout=timeout_time)

        return json.loads(resp.text)

    # TODO: Make max cachesize configurable?
    @lru_cache(maxsize=64)
    def get_coordinate(self, location_name: str, country_code: str) -> Coordinate:
        """Use Geocoding API to map a location_name and country_code to a coordinate.

        https://openweathermap.org/api/geocoding-api
        """

        parameters = {"q" : f"{location_name},{country_code}", "limit": 1}

        resp = self.owm_api_request(GEOCODING_API_BASE_URL, parameters)[0]

        return Coordinate(obj=resp)

    def get_current_weather(self, coord: Coordinate, units="metric") -> WeatherInformation:
        """Use Current Weather API to get current weather information.

        https://openweathermap.org/current
        """

        parameters = {"lat": coord.lat, "lon": coord.lon, "units": units}

        resp = self.owm_api_request(CURRENT_WEATHER_API_BASE_URL, parameters)

        return WeatherInformation(resp)

    def get_current_air_pollution(self, coord: Coordinate) -> AirPollutionInformation:
        """Use Current Air Pollution API to get current air pollution information.

        https://openweathermap.org/api/air-pollution
        """

        parameters = {"lat": coord.lat, "lon": coord.lon}

        resp = self.owm_api_request(CURRENT_AIR_POLLUTION_API_BASE_URL, parameters)

        return AirPollutionInformation(resp)

class Location:

    owm: OpenWeatherMap

    location_name: str
    country_code: str

    coord: Coordinate

    last_current_weather: Optional[WeatherInformation] = None
    last_current_air_pollution: Optional[AirPollutionInformation] = None

    def __init__(self, location_name: str, country_code: str, owm: OpenWeatherMap):
        self.location_name = location_name
        self.country_code = country_code
        self.owm = owm
        self.coord = self.owm.get_coordinate(location_name, country_code)

    def __str__(self):
        return f"Location(location_name={self.location_name}, country_code={self.country_code}, {self.coord})"

    def get_current_weather(self) -> WeatherInformation:
        """Get current weather information for this location.

        The information is cached internally, so that the OpenWeatherMap API
        will not be called more than once per location per ten minutes, since that
        is the internal update frequency of OpenWeatherMap.
            For more information, see https://openweathermap.org/appid#apicare.
        """

        if self.last_current_weather is None:
            self.last_current_weather = self.owm.get_current_weather(self.coord)
        else:
            time_since_last_update: timedelta = datetime.now() - self.last_current_weather.timestamp
            if time_since_last_update > timedelta(minutes=10):
                self.last_current_weather = self.owm.get_current_weather(self.coord)

        return self.last_current_weather

    def get_current_air_pollution(self) -> AirPollutionInformation:
        """Get current air pollution information for this location.

        The information is cached internally, so that the OpenWeatherMap API
        will not be called more than once per location per ten minutes, since that
        is the internal update frequency of OpenWeatherMap.
            For more information, see https://openweathermap.org/appid#apicare.
        """

        if self.last_current_air_pollution is None:
            self.last_current_air_pollution = self.owm.get_current_air_pollution(self.coord)
        else:
            time_since_last_update: timedelta = datetime.now() - self.last_current_air_pollution.timestamp
            if time_since_last_update > timedelta(minutes=10):
                self.last_current_air_pollution = self.owm.get_current_air_pollution(self.coord)

        return self.last_current_air_pollution

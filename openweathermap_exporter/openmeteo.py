"""
    openmeteo.py

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

import json
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Optional

import requests
from openweathermap import Coordinate

AIR_QUALITY_BASE_URL: str = "https://air-quality-api.open-meteo.com/v1/air-quality"
GEOCODING_BASE_URL: str = "https://geocoding-api.open-meteo.com/v1/search"

class OpenMeteoAirQualityForecast:

    request_datetime: datetime

    timestamps: list[datetime]
    pm10: list[Optional[float]]
    pm2_5: list[Optional[float]]
    co: list[Optional[float]]
    no2: list[Optional[float]]
    so2: list[Optional[float]]
    o3: list[Optional[float]]
    nh3: list[Optional[float]]
    aerosol_optical_depth: list[Optional[float]]
    dust: list[Optional[float]]
    uv_index: list[Optional[float]]
    uv_index_clear_sky: list[Optional[float]]
    alder_pollen: list[Optional[float]]
    birch_pollen: list[Optional[float]]
    grass_pollen: list[Optional[float]]
    mugwort_pollen: list[Optional[float]]
    olive_pollen: list[Optional[float]]
    ragweed_pollen: list[Optional[float]]
    european_aqi: list[Optional[float]]
    european_aqi_pm2_5: list[Optional[float]]
    european_aqi_pm10: list[Optional[float]]
    european_aqi_no2: list[Optional[float]]
    european_aqi_o3: list[Optional[float]]
    european_aqi_so2: list[Optional[float]]

    air_quality_values: dict[str, list[Optional[float]]]

    def __init__(self, request_datetime: datetime, obj: dict) -> None:
        """Parse air quality information based on the Open Meteo Air Quality API.
        
        https://open-meteo.com/en/docs/air-quality-api
        """

        self.request_datetime = request_datetime
        self.timestamps = [datetime.strptime(date, "%Y-%m-%dT%H:%M") for date in obj["hourly"]["time"]]
        self.pm10 = obj["hourly"]["pm10"]
        self.pm2_5 = obj["hourly"]["pm2_5"]
        self.co = obj["hourly"]["carbon_monoxide"]
        self.no2 = obj["hourly"]["nitrogen_dioxide"]
        self.so2 = obj["hourly"]["sulphur_dioxide"]
        self.o3 = obj["hourly"]["ozone"]
        self.nh3 = obj["hourly"]["ammonia"]
        self.aerosol_optical_depth = obj["hourly"]["aerosol_optical_depth"]
        self.dust = obj["hourly"]["dust"]
        self.uv_index = obj["hourly"]["uv_index"]
        self.uv_index_clear_sky = obj["hourly"]["uv_index_clear_sky"]
        self.alder_pollen = obj["hourly"]["alder_pollen"]
        self.birch_pollen = obj["hourly"]["birch_pollen"]
        self.grass_pollen = obj["hourly"]["grass_pollen"]
        self.mugwort_pollen = obj["hourly"]["mugwort_pollen"]
        self.olive_pollen = obj["hourly"]["olive_pollen"]
        self.ragweed_pollen = obj["hourly"]["ragweed_pollen"]
        self.european_aqi = obj["hourly"]["european_aqi"]
        self.european_aqi_pm2_5 = obj["hourly"]["european_aqi_pm2_5"]
        self.european_aqi_pm10 = obj["hourly"]["european_aqi_pm10"]
        self.european_aqi_no2 = obj["hourly"]["european_aqi_no2"]
        self.european_aqi_o3 = obj["hourly"]["european_aqi_o3"]
        self.european_aqi_so2 = obj["hourly"]["european_aqi_so2"]

        self.air_quality_values = {
            "pm10": self.pm10,
            "pm2_5": self.pm2_5,
            "co": self.co,
            "no2": self.no2,
            "so2": self.so2,
            "o3": self.o3,
            "nh3": self.nh3,
            "aerosol_optical_depth": self.aerosol_optical_depth,
            "dust": self.dust,
            "uv_index": self.uv_index,
            "uv_index_clear_sky": self.uv_index_clear_sky
        }

    def __str__(self) -> str:
        return f"OpenMeteoAirQualityForecast(timestamps={self.timestamps})"

class OpenMeteoCurrentAirQualityForecast:
    """Most recent forecast values for a specific datetime."""

    pm10: Optional[float]
    pm2_5: Optional[float]
    co: Optional[float]
    no2: Optional[float]
    so2: Optional[float]
    o3: Optional[float]
    nh3: Optional[float]
    aerosol_optical_depth: Optional[float]
    dust: Optional[float]
    uv_index: Optional[float]
    uv_index_clear_sky: Optional[float]
    alder_pollen: Optional[float]
    birch_pollen: Optional[float]
    grass_pollen: Optional[float]
    mugwort_pollen: Optional[float]
    olive_pollen: Optional[float]
    ragweed_pollen: Optional[float]
    european_aqi: Optional[float]
    european_aqi_pm2_5: Optional[float]
    european_aqi_pm10: Optional[float]
    european_aqi_no2: Optional[float]
    european_aqi_o3: Optional[float]
    european_aqi_so2: Optional[float]

    def __init__(self, index: int, forecast: OpenMeteoAirQualityForecast) -> None:
        self.pm10 = forecast.pm10[index]
        self.pm2_5 = forecast.pm2_5[index]
        self.co = forecast.co[index]
        self.no2 = forecast.no2[index]
        self.so2 = forecast.so2[index]
        self.o3 = forecast.o3[index]
        self.nh3 = forecast.nh3[index]
        self.aerosol_optical_depth = forecast.aerosol_optical_depth[index]
        self.dust = forecast.dust[index]
        self.uv_index = forecast.uv_index[index]
        self.uv_index_clear_sky = forecast.uv_index_clear_sky[index]
        self.alder_pollen = forecast.alder_pollen[index]
        self.birch_pollen = forecast.birch_pollen[index]
        self.grass_pollen = forecast.grass_pollen[index]
        self.mugwort_pollen = forecast.mugwort_pollen[index]
        self.olive_pollen = forecast.olive_pollen[index]
        self.ragweed_pollen = forecast.ragweed_pollen[index]
        self.european_aqi = forecast.european_aqi[index]
        self.european_aqi_pm2_5 = forecast.european_aqi_pm2_5[index]
        self.european_aqi_pm10 = forecast.european_aqi_pm10[index]
        self.european_aqi_no2 = forecast.european_aqi_no2[index]
        self.european_aqi_o3 = forecast.european_aqi_o3[index]
        self.european_aqi_so2 = forecast.european_aqi_so2[index]

class OpenMeteo:

    def __init__(self):
        pass

    def om_api_request(self, base_url: str, parameters: dict, timeout_time=10) -> dict:
        """Do an API request to an Open Meteo API endpoint."""

        resp = requests.get(base_url, params=parameters, timeout=timeout_time)

        return json.loads(resp.text)

    @lru_cache(maxsize=256)
    def get_coordinate(self, location_name) -> Coordinate:
        """Use Open Meteo Geocoding API to map a location_name to a coordinate.
        
        https://open-meteo.com/en/docs/geocoding-api
        """

        resp = self.om_api_request(
            GEOCODING_BASE_URL,
            {
                "name": location_name,
                "count": 1
            }
            )

        return Coordinate(obj=resp["results"][0])

    def get_air_quality(self, coord: Coordinate) -> OpenMeteoAirQualityForecast:
        """Retrieve an air quality forecast from the Open Meteo API.
        
        https://open-meteo.com/en/docs/air-quality-api
        """

        resp = self.om_api_request(
            AIR_QUALITY_BASE_URL,
            {
                "latitude": coord.lat,
                "longitude": coord.lon,
                "hourly": [
                    "pm10",
                    "pm2_5",
                    "carbon_monoxide",
                    "nitrogen_dioxide",
                    "sulphur_dioxide",
                    "ozone",
                    "ammonia",
                    "aerosol_optical_depth",
                    "dust",
                    "uv_index",
                    "uv_index_clear_sky",
                    "alder_pollen",
                    "birch_pollen",
                    "grass_pollen",
                    "mugwort_pollen",
                    "olive_pollen",
                    "ragweed_pollen",
                    "european_aqi",
                    "european_aqi_pm2_5",
                    "european_aqi_pm10",
                    "european_aqi_no2",
                    "european_aqi_o3",
                    "european_aqi_so2"
                ],
                #"timeformat": "unixtime",
                "timezone": "auto",
                "domains": "auto"
            }
        )

        return OpenMeteoAirQualityForecast(datetime.now(), resp)

class OpenMeteoLocation:
    om: OpenMeteo

    location_name: str
    country_code: str
    coord: Coordinate
    last_air_quality_forecast: Optional[OpenMeteoAirQualityForecast] = None

    def __init__(self, om: OpenMeteo, **kwargs):
        self.location_name = kwargs["location_name"]
        self.country_code = kwargs["country_code"]
        self.om = om

        try:
            self.coord = Coordinate(lat=kwargs["lat"], lon=kwargs["lon"])
        except KeyError:
            self.coord = self.om.get_coordinate(self.location_name)

    def __str__(self) -> str:
        return f"OpenMeteoLocation(location_name={self.location_name}, coord={self.coord})"

    def get_current_air_quality(self) -> OpenMeteoCurrentAirQualityForecast:
        """Get current air quality forecast."""

        if self.last_air_quality_forecast is None:
            self.last_air_quality_forecast = self.om.get_air_quality(self.coord)
        else:
            time_since_last_update = datetime.now() - self.last_air_quality_forecast.request_datetime
            # TODO: Make this 3 hours configurable
            if time_since_last_update > timedelta(hours=3):
                self.last_air_quality_forecast = self.om.get_air_quality(self.coord)

        now: datetime = datetime.now()
        now_hour = now.replace(minute=0, second=0, microsecond=0)

        index = self.last_air_quality_forecast.timestamps.index(now_hour)

        return OpenMeteoCurrentAirQualityForecast(index, self.last_air_quality_forecast)

"""
    __main__.py

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

from os import environ
from sys import exit
from time import sleep
from typing import Optional

import yaml
from prometheus_client import Gauge, start_http_server

from openweathermap import OpenWeatherMapLocation, OpenWeatherMap, WeatherInformation
from openmeteo import OpenMeteo, OpenMeteoLocation

label_names = ["latitude", "longitude", "location_country_code", "location_name"]

gauge_temp = Gauge(
    "weather_temp",
    "Outside temperature in degrees Celcius provided by OpenWeatherMap",
    labelnames=label_names
    )

gauge_temp_min = Gauge(
    "weather_temp_min",
    "Outside minimum temperature in degrees Celcius provided by OpenWeatherMap",
    labelnames=label_names
    )

gauge_temp_max = Gauge(
    "weather_temp_max",
    "Outside maximum temperature in degrees Celcius provided by OpenWeatherMap",
    labelnames=label_names
    )

gauge_temp_feels_like = Gauge(
    "weather_temp_feels_like",
    "Outside temperature adjusted to human perception in degrees Celcius provided by OpenWeatherMap",
    labelnames=label_names
)

gauge_pressure = Gauge(
    "weather_pressure",
    "Outside pressure in hPa provided by OpenWeatherMap",
    labelnames=label_names
    )

gauge_humidity = Gauge(
    "weather_humidity",
    "Outside relative humidity in % provided by OpenWeatherMap",
    labelnames=label_names
    )

gauge_visibility = Gauge(
    "weather_visibility",
    "Visibility in meters provided by OpenWeatherMap. The maximum value of the visibility is 10km.",
    labelnames=label_names
    )

gauge_wind_speed = Gauge(
    "weather_wind_speed",
    "Outside wind speed in m/s provided by OpenWeatherMap",
    labelnames=label_names
    )

gauge_wind_deg = Gauge(
    "weather_wind_deg",
    "Wind direction in degrees (meteorological) provided by OpenWeatherMap",
    labelnames=label_names
)

gauge_wind_gust = Gauge(
    "weather_wind_gust",
    "Wind gust in m/s",
    labelnames=label_names
)

gauge_cloudiness = Gauge(
    "weather_cloudiness",
    "Relative cloudiness in percentage provided by OpenWeatherMap",
    labelnames=label_names
)

gauge_rain_volume_1h = Gauge(
    "weather_rain_volume_1h",
    "Rain volume for the last 1 hour in mm provided by OpenWeatherMap",
    labelnames=label_names
)

gauge_rain_volume_3h = Gauge(
    "weather_rain_volume_3h",
    "Rain volume for the last 3 hours in mm provided by OpenWeatherMap",
    labelnames=label_names
)

gauge_snow_volume_1h = Gauge(
    "weather_snow_volume_1h",
    "Snow volume for the last 1 hour in mm provided by OpenWeatherMap",
    labelnames=label_names
)

gauge_snow_volume_3h = Gauge(
    "weather_snow_volume_3h",
    "Snow volume for the last 3 hours in mm provided by OpenWeatherMap",
    labelnames=label_names
)

gauge_air_quality_index = Gauge(
    "air_pollution_air_quality_index",
    """Air Quality Index provided by OpenWeatherMap. Possible values are: 1, 2, 3, 4, 5.
    Where 1 = Good, 2 = Fair, 3 = Moderate, 4 = Poor, 5 = Very Poor.""",
    labelnames=label_names
)

gauge_co = Gauge(
    "air_pollution_co",
    "Concentration of CO (carbon monoxide) in μg/m3 provided by OpenWeatherMap",
    labelnames=label_names
)

gauge_no = Gauge(
    "air_pollution_no",
    "Concentration of NO (nitrogen monoxide) in μg/m3 provided by OpenWeatherMap",
    labelnames=label_names
)

gauge_no2 = Gauge(
    "air_pollution_no2",
    "Concentration of NO2 (nitrogen dioxide) in μg/m3 provided by OpenWeatherMap",
    labelnames=label_names
)

gauge_o3 = Gauge(
    "air_pollution_o3",
    "Concentration of O3 (ozone) in μg/m3 provided by OpenWeatherMap",
    labelnames=label_names
)

gauge_so2 = Gauge(
    "air_pollution_so2",
    "Concentration of SO2 (sulphur dioxide) in μg/m3 provided by OpenWeatherMap",
    labelnames=label_names
)

gauge_pm2_5 = Gauge(
    "air_pollution_pm2_5",
    "Concentration of PM2.5 (fine particulate matter) in μg/m3 provided by OpenWeatherMap",
    labelnames=label_names
)

gauge_pm10 = Gauge(
    "air_pollution_pm10",
    "Concentration of PM10 (coarse particulate matter) in μg/m3 provided by OpenWeatherMap",
    labelnames=label_names
)

gauge_nh3 = Gauge(
    "air_pollution_nh3",
    "Concentration of NH3 (ammonia) in μg/m3 provided by OpenWeatherMap",
    labelnames=label_names
)

weather_gauges = {
    gauge_temp : "temp",
    gauge_temp_min : "temp_min",
    gauge_temp_max : "temp_max",
    gauge_temp_feels_like : "temp_feels_like",
    gauge_pressure : "pressure",
    gauge_humidity : "humidity",
    gauge_visibility : "visibility",
    gauge_wind_speed : "wind_speed",
    gauge_wind_deg : "wind_deg",
    gauge_wind_gust : "wind_gust",
    gauge_cloudiness : "cloudiness",
    gauge_rain_volume_1h : "rain_volume_1h",
    gauge_rain_volume_3h : "rain_volume_3h",
    gauge_snow_volume_1h : "snow_volume_1h",
    gauge_snow_volume_3h : "snow_volume_3h"
}

air_pollution_gauges = {
    gauge_air_quality_index : "air_quality_index",
    gauge_co : "co",
    gauge_no : "no",
    gauge_no2 : "no2",
    gauge_o3 : "o3",
    gauge_so2 : "so2",
    gauge_pm2_5 : "pm2_5",
    gauge_pm10 : "pm10",
    gauge_nh3 : "nh3"
}

om_gauge_pm10 = Gauge(
    "open_meteo_air_quality_pm10",
    "Particulate matter with diameter smaller than 10 µm (PM10) close to surface (10 meter above ground) in μg/m³.",
    labelnames=label_names
)

om_gauge_pm2_5 = Gauge(
    "open_meteo_air_quality_pm2_5",
    "Particulate matter with diameter smaller than 2.5 µm (PM2.5) close to surface (10 meter above ground) in μg/m³",
    labelnames=label_names
)

om_gauge_co = Gauge(
    "open_meteo_air_quality_co",
    "Carbon monoxide concentration in μg/m³ close to the surface (10 meter above ground)",
    labelnames=label_names
)

om_gauge_no2 = Gauge(
    "open_meteo_air_quality_no2",
    "Nitrogen dioxide concentration in μg/m³ close to the surface (10 meter above ground)",
    labelnames=label_names
)

om_gauge_so2 = Gauge(
    "open_meteo_air_quality_so2",
    "Sulphur dioxide concentration in μg/m³ close to the surface (10 meter above ground)",
    labelnames=label_names
)

om_gauge_o3 = Gauge(
    "open_meteo_air_quality_o3",
    "Ozone concentration in μg/m³ close to the surface (10 meter above ground)",
    labelnames=label_names
)

om_gauge_nh3 = Gauge(
    "open_meteo_air_quality_nh3",
    "Ammonia concentration in μg/m³ close to the surface (10 meter above ground)",
    labelnames=label_names
)

om_gauge_aerosol_optical_depth = Gauge(
    "open_meteo_air_quality_aerosol_optical_depth",
    "Aerosol optical depth at 550 nm of the entire atmosphere to indicate haze.",
    labelnames=label_names
)

om_gauge_dust = Gauge(
    "open_meteo_air_quality_dust",
    "Saharan dust particles close to surface level (10 meter above ground) in μg/m³.",
    labelnames=label_names
)

om_gauge_uv_index = Gauge(
    "open_meteo_air_quality_uv_index",
    "UV index considering clouds, conforming to the WHO definition",
    labelnames=label_names
)

om_gauge_uv_index_clear_sky = Gauge(
    "open_meteo_air_quality_uv_index_clear_sky",
    "UV index considering clear sky, conforming to the WHO definition",
    labelnames=label_names
)

om_gauge_alder_pollen = Gauge(
    "open_meteo_air_quality_alder_pollen",
    "Alder pollen concentration in grains/m³",
    labelnames=label_names
)

om_gauge_birch_pollen = Gauge(
    "open_meteo_air_quality_birch_pollen",
    "Birch pollen concentration in grains/m³",
    labelnames=label_names
)

om_gauge_grass_pollen = Gauge(
    "open_meteo_air_quality_grass_pollen",
    "Grass pollen concentration in grains/m³",
    labelnames=label_names
)

om_gauge_mugwort_pollen = Gauge(
    "open_meteo_air_quality_mugwort_pollen",
    "Mugwort pollen concentration in grains/m³",
    labelnames=label_names
)

om_gauge_olive_pollen = Gauge(
    "open_meteo_air_quality_olive_pollen",
    "Olive pollen concentration in grains/m³",
    labelnames=label_names
)

om_gauge_ragweed_pollen = Gauge(
    "open_meteo_air_quality_ragweed_pollen",
    "Ragweed pollen concentration in grains/m³",
    labelnames=label_names
)

om_gauge_eaqi = Gauge(
    "open_meteo_air_quality_european_aqi",
    "European Air Quality Index (AQI) calculated for different particulate matter and gases individually. The consolidated european_aqi returns the maximum of all individual indices. Ranges from 0-20 (good), 20-40 (fair), 40-60 (moderate), 60-80 (poor), 80-100 (very poor) and exceeds 100 for extremely poor conditions.",
    labelnames=label_names
)

om_gauge_eaqi_pm2_5 = Gauge(
    "open_meteo_air_quality_european_aqi_pm2_5",
    "European Air Quality Index (AQI) calculated for different particulate matter and gases individually. The consolidated european_aqi returns the maximum of all individual indices. Ranges from 0-20 (good), 20-40 (fair), 40-60 (moderate), 60-80 (poor), 80-100 (very poor) and exceeds 100 for extremely poor conditions.",
    labelnames=label_names
)

om_gauge_eaqi_pm10 = Gauge(
    "open_meteo_air_quality_european_aqi_pm10",
    "European Air Quality Index (AQI) calculated for different particulate matter and gases individually. The consolidated european_aqi returns the maximum of all individual indices. Ranges from 0-20 (good), 20-40 (fair), 40-60 (moderate), 60-80 (poor), 80-100 (very poor) and exceeds 100 for extremely poor conditions.",
    labelnames=label_names
)

om_gauge_eqai_no2 = Gauge(
    "open_meteo_air_quality_european_aqi_no2",
    "European Air Quality Index (AQI) calculated for different particulate matter and gases individually. The consolidated european_aqi returns the maximum of all individual indices. Ranges from 0-20 (good), 20-40 (fair), 40-60 (moderate), 60-80 (poor), 80-100 (very poor) and exceeds 100 for extremely poor conditions.",
    labelnames=label_names
)

om_gauge_eqai_o3 = Gauge(
    "open_meteo_air_quality_european_aqi_o3",
    "European Air Quality Index (AQI) calculated for different particulate matter and gases individually. The consolidated european_aqi returns the maximum of all individual indices. Ranges from 0-20 (good), 20-40 (fair), 40-60 (moderate), 60-80 (poor), 80-100 (very poor) and exceeds 100 for extremely poor conditions.",
    labelnames=label_names
)

om_gauge_eqai_so2 = Gauge(
    "open_meteo_air_quality_european_aqi_so2",
    "European Air Quality Index (AQI) calculated for different particulate matter and gases individually. The consolidated european_aqi returns the maximum of all individual indices. Ranges from 0-20 (good), 20-40 (fair), 40-60 (moderate), 60-80 (poor), 80-100 (very poor) and exceeds 100 for extremely poor conditions.",
    labelnames=label_names
)

open_meteo_air_quality_gauges = {
    om_gauge_pm10: "pm10",
    om_gauge_pm2_5: "pm2_5",
    om_gauge_co: "co",
    om_gauge_no2: "no2",
    om_gauge_so2: "so2",
    om_gauge_o3: "o3",
    om_gauge_nh3: "nh3",
    om_gauge_aerosol_optical_depth: "aerosol_optical_depth",
    om_gauge_dust: "dust",
    om_gauge_uv_index: "uv_index",
    om_gauge_uv_index_clear_sky: "uv_index_clear_sky",
    om_gauge_alder_pollen: "alder_pollen",
    om_gauge_birch_pollen: "birch_pollen",
    om_gauge_grass_pollen: "grass_pollen",
    om_gauge_mugwort_pollen: "mugwort_pollen",
    om_gauge_olive_pollen: "olive_pollen",
    om_gauge_ragweed_pollen: "ragweed_pollen",
    om_gauge_eaqi: "european_aqi",
    om_gauge_eaqi_pm2_5: "european_aqi_pm2_5",
    om_gauge_eaqi_pm10: "european_aqi_pm10",
    om_gauge_eqai_no2: "european_aqi_no2",
    om_gauge_eqai_o3: "european_aqi_o3",
    om_gauge_eqai_so2: "european_aqi_so2"
}

class Location:
    """Wrapper location class for access to both OpenWeatherMap and Open-Meteo data"""

    location_name: str
    country_code: str

    provided_lat: Optional[float] = None
    provided_lon: Optional[float] = None

    owml: OpenWeatherMapLocation
    oml: Optional[OpenMeteoLocation] = None
    open_meteo_enabled: bool = False

    def __init__(self, owm, **kwargs):
        """Create a generic Location class with support for all weather backends.

        Accepted keyword arguments:
        location_name: str
        country_code: str
        lat: float
        lon: float
        open_meteo_enabled: bool
        """
        self.location_name = kwargs["location_name"]
        self.country_code = kwargs["country_code"]

        try:
            self.provided_lat = kwargs["lat"]
            self.provided_lon = kwargs["lon"]
        except KeyError:
            pass

        if self.provided_lat is None:
            self.owml = OpenWeatherMapLocation(owm, location_name=self.location_name, country_code=self.country_code)
        else:
            self.owml = OpenWeatherMapLocation(
                owm,
                location_name=self.location_name,
                country_code=self.country_code,
                lat=self.provided_lat,
                lon=self.provided_lon
            )

        try:
            self.open_meteo_enabled = kwargs["open_meteo_enabled"]
        except KeyError:
            pass

        if self.open_meteo_enabled:
            om = OpenMeteo()
            if self.provided_lat is None:
                self.oml = OpenMeteoLocation(
                    om,
                    location_name=self.location_name,
                    country_code=self.country_code
                )
            else:
                self.oml = OpenMeteoLocation(
                    om,
                    location_name=self.location_name,
                    country_code=self.country_code,
                    lat=self.provided_lat,
                    lon=self.provided_lon
                )

# TODO: Maybe add a metric for total api calls done?
# meta_metrics = {}

def get_location_current_weather(location: OpenWeatherMapLocation, attr: str) -> float:
    """Helper function to easily get current weather data."""
    val = getattr(location.get_current_weather(), attr)
    if val is None:
        return 0

    return val

def get_location_current_air_pollution(location: OpenWeatherMapLocation, attr: str) -> float:
    """Helper function to easily get current air pollution data."""
    val = getattr(location.get_current_air_pollution(), attr)
    if val is None:
        return 0

    return val

def get_location_current_open_meteo_air_quality(location: OpenMeteoLocation, attr: str) -> float:
    val = getattr(location.get_current_air_quality(), attr)
    if val is None:
        return 0

    return val

def set_openweathermap_metrics(locations: list[OpenWeatherMapLocation]):
    """Set all defined OpenWeatherMap metrics to their newest value"""
    for loc in locations:
        # pylint: disable=C0206
        for gauge in weather_gauges:
            gauge.labels(
                location_name=loc.location_name,
                latitude=loc.coord.lat,
                longitude=loc.coord.lon,
                location_country_code=loc.country_code
            ).set(get_location_current_weather(loc, weather_gauges[gauge]))

        for gauge in air_pollution_gauges:
            gauge.labels(
                location_name=loc.location_name,
                latitude=loc.coord.lat,
                longitude=loc.coord.lon,
                location_country_code=loc.country_code
            ).set(get_location_current_air_pollution(loc, air_pollution_gauges[gauge]))

def set_openmeteo_metrics(locations: list[OpenMeteoLocation]) -> None:
    """Set all defined Open-Meteo metrics to their newest value"""

    for loc in locations:
        # pylint: disable=C0206
        for gauge in open_meteo_air_quality_gauges:
            gauge.labels(
                location_name=loc.location_name,
                latitude=loc.coord.lat,
                longitude=loc.coord.lon,
                location_country_code=loc.country_code
            ).set(get_location_current_open_meteo_air_quality(loc, open_meteo_air_quality_gauges[gauge]))

if __name__ == "__main__":

    config_filepath: str
    try:
        config_filepath = environ["OPENWEATHERMAP_EXPORTER_CONFIGURATION_FILE"]
    except:
        config_filepath = "openweathermap_exporter.yml"

    with open(config_filepath, 'r') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    api_key: str
    try:
        api_key = config["owm"]["api_key"]
    except (KeyError, TypeError):
        try:
            api_key = environ["OPENWEATHERMAP_API_KEY"]
        except KeyError:
            exit("Fatal error: no OpenWeatherMap API key provided."
            " Please set the environment variable OPENWEATHERMAP_API_KEY or provide the API key"
            " via the configuration file.")

    owm = OpenWeatherMap(api_key)
    open_meteo_enabled: bool = False
    try:
        open_meteo_enabled = config["prometheus_exporter"]["open_meteo_additional_data"]
    except KeyError:
        pass

    om: Optional[OpenMeteo] = None
    if open_meteo_enabled:
        om = OpenMeteo()

    locations: list[Location] = []
    for conf_location in config["prometheus_exporter"]["locations"]:
        try:
            locations.append(Location(
                owm,
                open_meteo_enabled=open_meteo_enabled,
                location_name=conf_location["name"],
                country_code=conf_location["cc"],
                lat=conf_location["lat"],
                lon=conf_location["lon"]
            ))
        except KeyError:
            locations.append(Location(
                owm,
                open_meteo_enabled=open_meteo_enabled,
                location_name=conf_location["name"],
                country_code=conf_location["cc"]
            ))

    openweathermap_locations = [ l.owml for l in locations ]

    if open_meteo_enabled:
        openmeteo_locations = [ l.oml for l in locations ]

    start_http_server(config["prometheus_exporter"]["port"], config["prometheus_exporter"]["host"])

    while True:
        set_openweathermap_metrics(openweathermap_locations)

        if open_meteo_enabled:
            set_openmeteo_metrics(openmeteo_locations)

        sleep(600)

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

from functools import partial
from time import sleep

import yaml
from prometheus_client import Gauge, start_http_server

from openweathermap import Location, OpenWeatherMap, WeatherInformation

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
    "Visibility in meters. The maximum value of the visibility is 10km",
    labelnames=label_names
    )

gauge_wind_speed = Gauge(
    "weather_wind_speed",
    "Outside wind speed in m/s provided by OpenWeatherMap",
    labelnames=label_names
    )

gauge_wind_deg = Gauge(
    "weather_wind_deg",
    "Wind direction, degrees (meteorological)",
    labelnames=label_names
)

gauge_wind_gust = Gauge(
    "weather_wind_gust",
    "Wind gust in m/s",
    labelnames=label_names
)

gauge_cloudiness = Gauge(
    "weather_cloudiness",
    "Relative cloudiness in percentage",
    labelnames=label_names
)

gauge_rain_volume_1h = Gauge(
    "weather_rain_volume_1h",
    "Rain volume for the last 1 hour, mm",
    labelnames=label_names
)

gauge_rain_volume_3h = Gauge(
    "weather_rain_volume_3h",
    "Rain volume for the last 3 hours, mm",
    labelnames=label_names
)

gauge_snow_volume_1h = Gauge(
    "weather_snow_volume_1h",
    "Snow volume for the last 1 hour, mm",
    labelnames=label_names
)

gauge_snow_volume_3h = Gauge(
    "weather_snow_volume_3h",
    "Snow volume for the last 3 hours, mm",
    labelnames=label_names
)

gauge_air_quality_index = Gauge(
    "air_pollution_air_quality_index",
    """Air Quality Index. Possible values are: 1, 2, 3, 4, 5.
    Where 1 = Good, 2 = Fair, 3 = Moderate, 4 = Poor, 5 = Very Poor.""",
    labelnames=label_names
)

gauge_co = Gauge(
    "air_pollution_co",
    "Concentration of CO (carbon monoxide) in μg/m3",
    labelnames=label_names
)

gauge_no = Gauge(
    "air_pollution_no",
    "Concentration of NO (nitrogen monoxide) in μg/m3",
    labelnames=label_names
)

gauge_no2 = Gauge(
    "air_pollution_no2",
    "Concentration of NO2 (nitrogen dioxide) in μg/m3",
    labelnames=label_names
)

gauge_o3 = Gauge(
    "air_pollution_o3",
    "Concentration of O3 (ozone) in μg/m3",
    labelnames=label_names
)

gauge_so2 = Gauge(
    "air_pollution_so2",
    "Concentration of SO2 (sulphur dioxide) in μg/m3",
    labelnames=label_names
)

gauge_pm2_5 = Gauge(
    "air_pollution_pm2_5",
    "Concentration of PM2.5 (fine particulate matter) in μg/m3",
    labelnames=label_names
)

gauge_pm10 = Gauge(
    "air_pollution_pm10",
    "Concentration of PM10 (coarse particulate matter) in μg/m3",
    labelnames=label_names
)

gauge_nh3 = Gauge(
    "air_pollution_nh3",
    "Concentration of NH3 (ammonia) in μg/m3",
    labelnames=label_names
)

weather_gauges = {
    gauge_temp : "temp",
    gauge_temp_min : "temp_min",
    gauge_temp_max : "temp_max",
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

# TODO: Maybe add a metric for total api calls done?
# meta_metrics = {}

def get_location_current_weather(location: Location, attr: str):
    """Helper function to easily get current weather data via a partial."""
    val = getattr(location.get_current_weather(), attr)
    if val is None:
        return 0

    return val

def get_location_current_air_pollution(location: Location, attr: str):
    """Helper function to easily get current air pollution data via a partial."""
    val = getattr(location.get_current_air_pollution(), attr)
    if val is None:
        return 0

    return val

def set_metrics(locations: list[Location]):
    """Set all defined metrics to their newest value"""
    for loc in locations:
        # pylint: disable=C0206
        for gauge in weather_gauges:
            gauge.labels(
                location_name=loc.location_name,
                latitude=loc.coord.lat,
                longitude=loc.coord.lon,
                location_country_code=loc.country_code
            ).set(partial(get_location_current_weather, loc, weather_gauges[gauge])())

        for gauge in air_pollution_gauges:
            gauge.labels(
                location_name=loc.location_name,
                latitude=loc.coord.lat,
                longitude=loc.coord.lon,
                location_country_code=loc.country_code
            ).set(partial(get_location_current_air_pollution, loc, air_pollution_gauges[gauge])())

if __name__ == "__main__":

    # TODO: Let config path be passed via command line argument
    with open("openweathermap_exporter.yml", 'r') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    owm = OpenWeatherMap(config["owm"]["api_key"])

    locations: list[Location] = []
    for conf_location in config["exporter"]["locations"]:
        locations.append(Location(conf_location["name"], conf_location["cc"], owm))

    start_http_server(config["exporter"]["port"])

    # Not sure why this is required?
    while True:
        set_metrics(locations)
        sleep(600)

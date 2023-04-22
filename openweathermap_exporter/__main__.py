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

import yaml
from prometheus_client import Gauge, start_http_server

from openweathermap import Location, OpenWeatherMap, WeatherInformation

label_names = ["latitude", "longitude", "location_country_code", "location_name"]

gauge_temp = Gauge("weather_temp", "Outside temperature in degrees Celcius provided by OpenWeatherMap", labelnames=label_names)
gauge_temp_min = Gauge("weather_temp_min", "Outside minimum temperature in degrees Celcius provided by OpenWeatherMap", labelnames=label_names)
gauge_temp_max = Gauge("weather_temp_max", "Outside maximum temperature in degrees Celcius provided by OpenWeatherMap", labelnames=label_names)
gauge_pressure = Gauge("weather_pressure", "Outside pressure in hPa provided by OpenWeatherMap", labelnames=label_names)
gauge_humidity = Gauge("weather_humidity", "Outside relative humidity in % provided by OpenWeatherMap", labelnames=label_names)
gauge_wind_speed = Gauge("weather_wind_speed", "Outside wind speed in m/s provided by OpenWeatherMap", labelnames=label_names)

if __name__ == "__main__":

    # TODO: Let config path be passed via command line argument
    with open("openweathermap_exporter.yml", 'r') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    owm = OpenWeatherMap(config["owm"]["api_key"])

    locations: list[Location] = []
    for conf_location in config["exporter"]["locations"]:
        locations.append(Location(conf_location["name"], conf_location["cc"], owm))

    for loc in locations:
        gauge_temp.labels(
            location_name=loc.location_name,
            latitude=loc.coord.lat,
            longitude=loc.coord.lon,
            location_country_code=loc.country_code
            ).set_function(lambda : loc.get_weather(owm).temp)
        gauge_temp_min.labels(
            location_name=loc.location_name,
            latitude=loc.coord.lat,
            longitude=loc.coord.lon,
            location_country_code=loc.country_code
            ).set_function(lambda : loc.get_weather(owm).temp_min)
        gauge_temp_max.labels(
            location_name=loc.location_name,
            latitude=loc.coord.lat,
            longitude=loc.coord.lon,
            location_country_code=loc.country_code
            ).set_function(lambda : loc.get_weather(owm).temp_max)
        gauge_pressure.labels(
            location_name=loc.location_name,
            latitude=loc.coord.lat,
            longitude=loc.coord.lon,
            location_country_code=loc.country_code
            ).set_function(lambda : loc.get_weather(owm).pressure)
        gauge_humidity.labels(
            location_name=loc.location_name,
            latitude=loc.coord.lat,
            longitude=loc.coord.lon,
            location_country_code=loc.country_code
            ).set_function(lambda : loc.get_weather(owm).humidity)

    start_http_server(config["exporter"]["port"])

    # Not sure why this is required?
    while True:
        pass

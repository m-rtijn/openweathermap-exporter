import configparser
from prometheus_client import Gauge, start_http_server

from openweathermap import *

label_names = ["latitude", "longitude", "location_country_code", "location_name"]

gauge_temperature = Gauge("weather_temperature", "Outside temperature in degrees Celcius provided by OpenWeatherMap", labelnames=label_names)


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("openweathermap_exporter.conf")

    owm = OpenWeatherMap()

    loc = Location("Den Haag", "NL", owm)

    gauge_temperature.labels(
        location_name=loc.location_name,
        latitude=loc.coord.lat,
        longitude=loc.coord.lon,
        location_country_code=loc.country_code
        ).set_function(lambda : loc.get_weather(owm).temp)

    start_http_server(8080)

    # Not sure why this is required?
    while True:
        pass
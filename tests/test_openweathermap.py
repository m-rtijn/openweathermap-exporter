import unittest

import yaml
from os import environ

from openweathermap_exporter.openweathermap import OpenWeatherMap, OpenWeatherMapLocation, WeatherInformation, AirPollutionInformation

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

owm: OpenWeatherMap = OpenWeatherMap(api_key)

l: OpenWeatherMapLocation = OpenWeatherMapLocation(owm, location_name="Utrecht", country_code="NL")

print(l.get_current_air_pollution())

class OpenWeatherMapTestCases(unittest.TestCase):

    def test_get_current_air_pollution(self):
        self.assertIsNotNone(l.get_current_air_pollution())

    def test_get_current_weather(self):
        self.assertIsNotNone(l.get_current_weather())

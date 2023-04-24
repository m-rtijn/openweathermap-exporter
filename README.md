# openweathermap_exporter
[![Code quality](https://github.com/m-rtijn/argostime/actions/workflows/code_quality.yml/badge.svg?branch=master)](https://github.com/m-rtijn/argostime/actions/workflows/code_quality.yml) ![GitHub](https://img.shields.io/github/license/m-rtijn/argostime)

A simple Prometheus exporter for OpenWeatherMap. Using this exporter requires a valid API key from OpenWeatherMap. The free API key is sufficient for usage of this exporter.

# Features

* Supports Current Weather and Current Air Pollution API's.
* Multiple locations can be specified in YAML-config, either by name or by coordinate.
* Caches API results so no redundant API calls are made.

# Metrics

| Name | Description |
|---|---|
| `weather_temp` | Outside temperature in degrees Celcius |
| `weather_temp_min` | Outside minimum temperature in degrees Celcius |
| `weather_temp_max` | Outside maximum temperature in degrees Celcius |
| `weather_temp_feels_like` | Outside temperature adjusted to human perception in degrees Celcius |
| `weather_pressure` | Outside pressure in hPa |
| `weather_humidity` | Outside relative humidity in % |
| `weather_visibility` | Visibility in meters. The maximum value of the visibility is 10km |
| `weather_wind_speed` | Outside wind speed in m/s |
| `weather_wind_deg` | Wind direction, degrees (meteorological) |
| `weather_wind_gust` | Wind gust in m/s |
| `weather_cloudiness` | Relative cloudiness in percentage |
| `weather_rain_volume_1h` | Rain volume for the last 1 hour, mm |
| `weather_rain_volume_3h` | Rain volume for the last 3 hours, mm |
| `weather_snow_volume_1h` | Snow volume for the last 1 hour, mm |
| `weather_snow_volume_3h` | Snow volume for the last 3 hours, mm |
| `air_pollution_air_quality_index` | Air Quality Index. Possible values are: 1, 2, 3, 4, 5. Where 1 = Good, 2 = Fair, 3 = Moderate, 4 = Poor, 5 = Very Poor. |
| `air_pollution_co` | Concentration of CO (carbon monoxide) in μg/m3 |
| `air_pollution_no` | Concentration of NO (nitrogen monoxide) in μg/m3 |
| `air_pollution_no2` | Concentration of NO2 (nitrogen dioxide) in μg/m3 |
| `air_pollution_o3` | Concentration of O3 (ozone) in μg/m3 |
| `air_pollution_so2` | Concentration of SO2 (sulphur dioxide) in μg/m3 |
| `air_pollution_pm2_5` | Concentration of PM2.5 (fine particulate matter) in μg/m3 |
| `air_pollution_pm10` | Concentration of PM10 (coarse particulate matter) in μg/m3 |
| `air_pollution_nh3` | Concentration of NH3 (ammonia) in μg/m3 |

# License

Copyright 2023 Martijn

openweathermap_exporter is available under the GNU Affero General Public License, version 3, or (at
your option), any later version.
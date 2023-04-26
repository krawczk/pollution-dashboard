from datetime import datetime
from datetime import datetime
from typing import Union
import logging
import pandas as pd
import requests

from config import MEASURES


def get_gios_pollution_data(is_long=False):
    pollution_data = []
    all_station_data = _fetch_gios_all_station_data()
    today_date = datetime.now().strftime("%Y-%m-%d %H")

    for station_id in all_station_data["id"]:
        station_data = all_station_data[all_station_data["id"] == station_id]
        station_pollution_df = pd.DataFrame()
        try:
            sensors_id = _fetch_gios_sensor_data(station_id)["id"]
        except KeyError:
            pass
        for sensor_id in sensors_id:
            sensor_data = _fetch_gios_pollution_data_from_sensor(sensor_id)
            if not isinstance(sensor_data, pd.DataFrame):
                logging.warning(f"No available sensor data for given {station_id}")
            sensor_data.rename(columns={"key": "measure", "value": "pollution_value"}, inplace=True)
            station_pollution_df = pd.concat([station_pollution_df, sensor_data])

        # Remove any nan values
        station_pollution_df.dropna(inplace=True)

        # Filter the date after obtaining all the data from sensor_ids for given station
        station_pollution_df = station_pollution_df[station_pollution_df["date"].str.contains(today_date)].sort_values(by=["date"])
        station_pollution_df["date"] = pd.to_datetime(station_pollution_df["date"]).dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Add station id and name to dataframe
        station_pollution_df["name"] = station_data["stationName"].iloc[0]

        # Add the location data to the dataframe
        lat = station_data["gegrLat"].iloc[0]
        lon = station_data["gegrLon"].iloc[0]
        for measure in station_pollution_df["measure"]:
            if measure in MEASURES:
                station_pollution_data_dict = {"Name": station_data[station_data["id"] == station_id]["stationName"].iloc[0],
                                  "Date": today_date, "LAT": lat, "LON": lon}
                if is_long:
                    station_pollution_data_dict["MEASURE"] = measure
                else:
                    df_filtered_by_measure = station_pollution_df[station_pollution_df["measure"] == measure]
                    station_pollution_data_dict[measure] = df_filtered_by_measure["pollution_value"].values[0]
                pollution_data.append(station_pollution_data_dict)
    pollution_df = pd.DataFrame.from_dict(pollution_data)
    return pollution_df


def _fetch_gios_all_station_data() -> Union[pd.DataFrame, str]:
    r = requests.get("https://api.gios.gov.pl/pjp-api/rest/station/findAll")
    if r.status_code == 200:
        return pd.DataFrame(r.json())
    else:
        return r.text


def _fetch_gios_sensor_data(station_id: int) -> Union[pd.DataFrame, str]:
    r = requests.get(f"https://api.gios.gov.pl/pjp-api/rest/station/sensors/{station_id}")
    if r.status_code == 200:
        return pd.DataFrame(r.json())
    else:
        return r.text


def _fetch_gios_pollution_data_from_sensor(sensor_id: int) -> Union[pd.DataFrame, str]:
    r = requests.get(f"https://api.gios.gov.pl/pjp-api/rest/data/getData/{sensor_id}")
    if r.status_code == 200:
        df = pd.DataFrame(r.json())
        df = pd.concat([df, df["values"].apply(pd.Series)], axis=1).drop(columns="values")
        return df
    else:
        return r.text

from datetime import datetime
from datetime import datetime
from typing import Union

import pandas as pd
import requests

from config import MEASURES


def get_gios_pollution_data():
    pollution_df = pd.DataFrame()
    station_data = _fetch_gios_station_data()
    # Filter the station data to remove extensive usage of data with getting all the stations
    station_data = station_data.head(10)
    daily_data = []
    today_date = datetime.now().strftime("%Y-%m-%d")

    for station_id in station_data["id"]:
        station_df = pd.DataFrame()
        try:
            sensors_id = _fetch_gios_sensor_data(station_id)["id"]
        except KeyError:
            pass
        for sensor_id in sensors_id:
            sensor_data = _fetch_gios_data(sensor_id)
            sensor_data.rename(columns={"key": "measure", "value": "pollution_value"}, inplace=True)
            station_df = pd.concat([station_df, sensor_data])

        # Remove any nan values
        station_df.dropna(inplace=True)

        # Filter the date after obtaining all the data from sensor_ids for given station
        station_df = station_df[station_df["date"].str.contains(today_date)].sort_values(by=["date"])
        station_df["date"] = pd.to_datetime(station_df["date"]).dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Add station id and name to dataframe
        station_df["name"] = station_data[station_data["id"] == station_id]["stationName"].iloc[0]

        # Add the location data to the dataframe
        lat = station_data[station_data["id"] == station_id]["gegrLat"].iloc[0]
        lon = station_data[station_data["id"] == station_id]["gegrLon"].iloc[0]

        for filter_date in station_df["date"].unique():
            pollution_data = {"Name": station_data[station_data["id"] == station_id]["stationName"].iloc[0],
                              "Date": filter_date, "LAT": lat, "LON": lon}
            df_filtered_by_date = station_df[station_df["date"] == filter_date]
            for measure in df_filtered_by_date["measure"]:
                if measure in MEASURES:
                    df_filtered_by_measure = df_filtered_by_date[df_filtered_by_date["measure"] == measure]
                    pollution_data[measure] = df_filtered_by_measure["pollution_value"].values[0]
            daily_data.append(pollution_data)

    pollution_df = pollution_df.from_dict(daily_data)
    return pollution_df


def _fetch_gios_station_data() -> Union[pd.DataFrame, str]:
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


def _fetch_gios_data(sensor_id: int) -> Union[pd.DataFrame, str]:
    r = requests.get(f"https://api.gios.gov.pl/pjp-api/rest/data/getData/{sensor_id}")
    if r.status_code == 200:
        df = pd.DataFrame(r.json())
        df = pd.concat([df, df["values"].apply(pd.Series)], axis=1).drop(columns="values")
        return df
    else:
        return r.text

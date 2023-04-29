import logging
from datetime import datetime, timedelta
from typing import Union
import pandas as pd
import requests
from config import MEASURES


def get_gios_pollution_data(is_long=False):
    pollution_data = []
    all_station_data = _fetch_gios_all_station_data()
    for station_id in all_station_data["id"]:
        station_data = all_station_data[all_station_data["id"] == station_id]
        station_pollution_df = pd.DataFrame()
        try:
            sensors_id = _fetch_gios_sensor_data(station_id)["id"]
        except KeyError:
            logging.warning(f"Failed to get sensor_id for {station_id}")
            continue
        for sensor_id in sensors_id:
            sensor_data = _fetch_gios_pollution_data_from_sensor(sensor_id)
            if not isinstance(sensor_data, pd.DataFrame):
                logging.warning(f"No available sensor data for sensor {sensor_id} data for station {station_id}")
                continue
            station_pollution_df = pd.concat([station_pollution_df, sensor_data])

        station_pollution_df["date"] = pd.to_datetime(station_pollution_df["date"]).dt.strftime("%Y-%m-%d")
        station_pollution_df["name"] = station_data["stationName"].iloc[0]
        lat = station_data["gegrLat"].iloc[0]
        lon = station_data["gegrLon"].iloc[0]
        for measure in station_pollution_df["key"]:
            if measure in MEASURES:
                station_pollution_data_dict = {
                    "Name": station_data[station_data["id"] == station_id]["stationName"].iloc[0],
                    "Date": datetime.now().strftime("%Y-%m-%d"), "LAT": lat, "LON": lon}
                if is_long:
                    station_pollution_data_dict["Measure"] = measure
                    station_pollution_data_dict["Pollution_Value"] = \
                        station_pollution_df[station_pollution_df["key"] == measure]["value"].values[0]
                else:
                    df_filtered_by_measure = station_pollution_df[station_pollution_df["key"] == measure]
                    station_pollution_data_dict[measure] = df_filtered_by_measure["value"].values[0]
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
        if "date" in df:
            current_day = datetime.now().strftime("%Y-%m-%d")
            df = df[(df["date"] > current_day) & (df["date"] < (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H"))]
            df_to_report = df.groupby(["key"]).mean(numeric_only=True).reset_index()
            df_to_report["date"] = current_day
            return df_to_report
        else:
            return f"Sensor {sensor_id} updated with invalid date"
    else:
        return r.text

import json
import os
from datetime import datetime
from typing import Union

import pandas as pd
import requests

TOKEN = os.environ.get("TOKEN")
FEATURE_SERVICE_URL = os.environ.get("FEATURE_SERVICE_URL")
CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
MEASURES = ["PM10", "PM2.5", "CO", "SO2", "NO2"]


def generate_oauth_token(client_id: str, client_secret: str) -> str:
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    r = requests.get("https://www.arcgis.com/sharing/rest/oauth2/token", params=params)

    if r.status_code == 200:
        token = r.json()["access_token"]
        return token
    else:
        return r.text


def fetch_gios_station_data() -> Union[pd.DataFrame, str]:
    r = requests.get("https://api.gios.gov.pl/pjp-api/rest/station/findAll")

    if r.status_code == 200:
        return pd.DataFrame(r.json())
    else:
        return r.text


def fetch_gios_sensor_data(station_id: int) -> Union[pd.DataFrame, str]:
    r = requests.get(f"https://api.gios.gov.pl/pjp-api/rest/station/sensors/{station_id}")

    if r.status_code == 200:
        return pd.DataFrame(r.json())
    else:
        return r.text


def fetch_gios_data(sensor_id: int) -> Union[pd.DataFrame, str]:
    r = requests.get(f"https://api.gios.gov.pl/pjp-api/rest/data/getData/{sensor_id}")

    if r.status_code == 200:
        df = pd.DataFrame(r.json())
        df = pd.concat([df, df["values"].apply(pd.Series)], axis=1).drop(columns="values")
        return df
    else:
        return r.text


def get_all_pollution_data(feature_service_url: str) -> Union[dict, str]:
    # Set the query parameters
    params = {
        "where": "POLLUTION_VALUE>0",  # Filter criteria
        "outFields": "*",  # List of fields to include in the response
        "returnGeometry": "true",  # Include geometry in the response
        "f": "json"  # Response format
    }

    # Send a GET request to the feature service
    response = requests.get(feature_service_url + "/query", params=params)

    # Check the status code of the response
    if response.status_code == 200:
        # Print the response data
        return response.json()
    else:
        # Print an error message
        return f"Error retrieving features: {response.status_code} {response.reason}"


def post_station_data_to_arcgis_online(df: pd.DataFrame, feature_service_url: str, token: str) -> Union[
    dict, str]:
    features = []

    # Iterate over the rows in the dataframe
    for index, row in df.iterrows():
        # Get the data for the current row
        name = row["Name"]
        date = row["Date"]
        lat = row["LAT"]
        lon = row["LON"]
        pm10 = row.get("PM10")
        pm25 = row.get("PM2.5")
        so2 = row.get("SO2")
        no2 = row.get("NO2")
        co = row.get("CO")

        # Send a POST request to the feature service to add a new feature
        features.append({
            "attributes": {
                "Name": name,
                "Date": date,
                "LAT": lat,
                "LON": lon,
                "PM10": pm10,
                "PM25": pm25,
                "CO": co,
                "SO2": so2,
                "NO2": no2
            },
            "geometry": {
                "x": lon,
                "y": lat,
                "spatialReference": {
                    "wkid": 4326
                }
            }
        })

    data = {
        "f": "json",
        "token": token,
        "features": json.dumps(features)
    }

    headers = {
        "Content-Type": "application/json",
    }

    response = requests.post(feature_service_url + "/addFeatures", data=data)

    # Check the status code of the response to make sure the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        return f"Error adding feature: {response.status_code} {response.reason}"


def delete_all_features(feature_service_url: str, token: str) -> Union[dict, str]:
    # Set the parameters for the query operation
    params = {
        "where": "1=1",  # This will return all features
        "returnIdsOnly": True,  # We only need the object IDs of the features
        "f": "json",  # Set the response format to JSON,
        "token": token
    }

    headers = {
        "Content-Type": "application/json",
    }

    # Send a GET request to the query operation
    response = requests.get(feature_service_url + "/query", params=params, headers=headers)

    # Check the status code of the response to make sure the request was successful
    if response.status_code == 200:
        # Get the object IDs of the features from the response
        object_ids = response.json()["objectIds"]

        # If there are no features, return a message
        if len(object_ids) == 0:
            return "There are no features to delete."

        # Set the chunk size
        chunk_size = int(len(object_ids) / 10)

        # Iterate over the object IDs in chunks
        for i in range(0, len(object_ids), chunk_size):
            # Get the current chunk of object IDs
            object_ids_chunk = object_ids[i:i + chunk_size]

            # Set the parameters for the deleteFeatures operation
            params = {
                "objectIds": ",".join(str(x) for x in object_ids_chunk),  # Convert the object IDs to a string
                "f": "json",  # Set the response format to JSON
                "token": token
            }

            # Send a POST request to the deleteFeatures operation
            response = requests.post(feature_service_url + "/deleteFeatures", params=params, headers=headers)

            # Check the status code of the response to make sure the request was successful
            if response.status_code != 200:
                return f"Error when performing a delete operation: {response.status_code} {response.reason}"


if __name__ == "__main__":
    print("Starting to execute script")

    df_to_report = pd.DataFrame()

    station_data = fetch_gios_station_data()

    station_data = station_data.head(20)

    daily_data = []

    today_date = datetime.now().strftime("%Y-%m-%d")

    token = generate_oauth_token(CLIENT_ID, CLIENT_SECRET)

    for station_id in station_data["id"]:
        station_df = pd.DataFrame()

        try:
            sensors_id = fetch_gios_sensor_data(station_id)["id"]
        except KeyError:
            pass

        for sensor_id in sensors_id:
            sensor_data = fetch_gios_data(sensor_id)

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

    df_to_report = df_to_report.from_dict(daily_data)

    response = post_station_data_to_arcgis_online(df_to_report, FEATURE_SERVICE_URL, token)

    print("Script executed successfully")

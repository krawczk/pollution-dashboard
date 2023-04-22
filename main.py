from datetime import datetime
import pandas as pd

from config import CLIENT_ID, CLIENT_SECRET, MEASURES, FEATURE_SERVICE_URL
from steps_definitions import fetch_gios_station_data, generate_oauth_token, fetch_gios_sensor_data, fetch_gios_data, \
    post_station_data_to_arcgis_online
from datetime import datetime

import pandas as pd

from config import CLIENT_ID, CLIENT_SECRET, MEASURES, FEATURE_SERVICE_URL
from steps_definitions import fetch_gios_station_data, generate_oauth_token, fetch_gios_sensor_data, fetch_gios_data, \
    post_station_data_to_arcgis_online

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

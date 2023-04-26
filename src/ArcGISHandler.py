import json
from typing import Union

import pandas as pd
import requests
from arcgis import GIS
from arcgis.features import FeatureSet, FeatureLayer

from config import USERNAME, PASSWORD, POLLUTION_MAP_ID, POLLUTION_DATA_ID, POLLUTION_DASHBOARD_ID


def get_feature_set_from_pollution_data(pollution_df) -> list:
    feature_set = []
    for index, row in pollution_df.iterrows():
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

        feature_set.append({
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
    return feature_set


def post_pollution_data_to_arcgis_online(pollution_df: pd.DataFrame, feature_service_url: str, token: str) -> Union[
    dict, str]:
    feature_set = get_feature_set_from_pollution_data(pollution_df)
    data = {
        "f": "json",
        "token": token,
        "features": json.dumps(feature_set)
    }
    response = requests.post(feature_service_url + "/addFeatures", data=data)
    if response.status_code == 200:
        return response.json()
    else:
        return f"Error adding feature: {response.status_code} {response.reason}"


def update_pollution_data_with_new_feature_set(pollution_df, pollution_data_feature):
    new_feature_set = get_feature_set_from_pollution_data(pollution_df)
    assert new_feature_set, "Empty feature set"
    pollution_data_feature.edit_features(adds=new_feature_set)


class ArcGISHandler:
    gis = GIS("https://www.arcgis.com", username=USERNAME, password=PASSWORD)

    def __init__(self):
        pass

    def get_pollution_data_feature_layer(self) -> pd.DataFrame:
        pollution_data_feature_item = self.gis.content.get(POLLUTION_DATA_ID)
        assert pollution_data_feature_item.title == "Pollution Data"
        assert pollution_data_feature_item.owner == "krawczyk_agh_ust"
        pollution_data_feature_layer = FeatureLayer(pollution_data_feature_item.layers[0].url, self.gis)
        return pollution_data_feature_layer

    def get_pollution_map(self) -> pd.DataFrame:
        pollution_map = self.gis.content.get(POLLUTION_MAP_ID)
        assert pollution_map.title == "Pollution Map"
        assert pollution_map.owner == "krawczyk_agh_ust"
        return pollution_map

    def get_pollution_dashboard(self) -> pd.DataFrame:
        pollution_dashboard = self.gis.content.get(POLLUTION_DASHBOARD_ID)
        assert pollution_dashboard.title == "Pollution Map"
        assert pollution_dashboard.owner == "krawczyk_agh_ust"
        return pollution_dashboard

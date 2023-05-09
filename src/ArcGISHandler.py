import json
from typing import Union
import pandas as pd
import requests
from arcgis import GIS
from arcgis.features import FeatureLayer
from config import USERNAME, PASSWORD, POLLUTION_MAP_ID, POLLUTION_DATA_ID, POLLUTION_DASHBOARD_ID, \
    POLLUTION_DATA_LONG_ID


class ArcGISHandler:
    def __init__(self, username: str = USERNAME, password: str = PASSWORD):
        self.gis = GIS("https://www.arcgis.com", username=username, password=password)

    @staticmethod
    def get_feature_set_from_pollution_data(pollution_df, is_long=False) -> list:
        feature_set = []
        for index, row in pollution_df.iterrows():
            attributes = {
                "Name": row.get("Name"),
                "Date": row.get("Date"),
                "LAT": row.get("LAT"),
                "LON": row.get("LON"),
            }

            if is_long:
                attributes["Measure"] = row.get("Measure")
                attributes["Pollution_Value"] = row.get("Pollution_Value")
            else:
                attributes["PM10"] = row.get("PM10")
                attributes["PM25"] = row.get("PM25")
                attributes["SO2"] = row.get("SO2")
                attributes["NO2"] = row.get("NO2")

            feature_set.append({
                "attributes": attributes,
                "geometry": {
                    "x": row.get("LON"),
                    "y": row.get("LAT"),
                    "spatialReference": {
                        "wkid": 4326
                    }
                }
            })
        return feature_set

    @staticmethod
    def post_pollution_data_to_arcgis_online(pollution_df: pd.DataFrame, feature_service_url: str, token: str) -> Union[
        dict, str]:
        feature_set = pollution_df.get_feature_set_from_pollution_data(pollution_df)
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

    @staticmethod
    def update_pollution_data_with_new_feature_set(pollution_df, pollution_data_feature, is_long=False):
        new_feature_set = ArcGISHandler.get_feature_set_from_pollution_data(pollution_df, is_long)
        assert new_feature_set, "Empty feature set"
        pollution_data_feature.edit_features(adds=new_feature_set)

    def get_pollution_map(self) -> pd.DataFrame:
        pollution_map = self.gis.content.get(POLLUTION_MAP_ID)
        assert pollution_map.title == "Pollution Map"
        assert pollution_map.owner == "krawczyk_agh_ust"
        return pollution_map

    def get_pollution_dashboard(self) -> pd.DataFrame:
        pollution_dashboard = self.gis.content.get(POLLUTION_DASHBOARD_ID)
        assert pollution_dashboard.title == "Pollution Dashboard"
        assert pollution_dashboard.owner == "krawczyk_agh_ust"
        return pollution_dashboard

    def get_pollution_data(self, is_long: bool = False) -> FeatureLayer:
        feature_layer = self.get_pollution_data_feature_layer(is_long)
        features = feature_layer.query()
        return features.sdf

    def add_pollution_data(self, pollution_df: pd.DataFrame, is_long: bool = False) -> None:
        feature_layer = self.get_pollution_data_feature_layer(is_long)
        self.update_pollution_data_with_new_feature_set(pollution_df, feature_layer, is_long)

    def delete_all_pollution_data(self, is_long: bool = False):
        feature_layer = self.get_pollution_data_feature_layer(is_long)
        object_ids = ",".join(str(feature.attributes["OBJECTID"]) for feature in feature_layer.query().features)
        feature_layer.delete_features(where=f"OBJECTID IN ({object_ids})")

    def get_pollution_data_feature_layer(self, is_long=False) -> FeatureLayer:
        pollution_data_id = POLLUTION_DATA_LONG_ID if is_long else POLLUTION_DATA_ID
        pollution_data_feature_item = self.gis.content.get(pollution_data_id)
        assert pollution_data_feature_item.title == "Pollution Data Long"
        assert pollution_data_feature_item.owner == "krawczyk_agh_ust"
        pollution_data_feature_layer = FeatureLayer(pollution_data_feature_item.layers[0].url, self.gis)
        return pollution_data_feature_layer



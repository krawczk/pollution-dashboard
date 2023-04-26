from arcgis.features import FeatureLayer

from ArcGISHandler import ArcGISHandler, update_pollution_data_with_new_feature_set
from gios_steps_definitions import get_gios_pollution_data

if __name__ == "__main__":
    print("Starting to execute script")
    # token = generate_oauth_token(CLIENT_ID, CLIENT_SECRET)
    pollution_df = get_gios_pollution_data(is_long=True)

    arcgis_handler = ArcGISHandler()

    pollution_map = arcgis_handler.get_pollution_map()
    pollution_data_feature_layer = arcgis_handler.get_pollution_data_feature_layer(is_long=True)
    pollution_dashboard = arcgis_handler.get_pollution_dashboard()

    pollution_data_feature_layer.delete_features(where="1=1")

    update_pollution_data_with_new_feature_set(pollution_df, pollution_data_feature_layer, is_long=True)

    # response = post_station_data_to_arcgis_online(pollution_df, FEATURE_SERVICE_URL, token)
    print("Script executed successfully")

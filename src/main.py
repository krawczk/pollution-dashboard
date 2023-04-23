from ArcGISHandler import ArcGISHandler
from gios_steps_definitions import get_gios_pollution_data

if __name__ == "__main__":
    print("Starting to execute script")
    # token = generate_oauth_token(CLIENT_ID, CLIENT_SECRET)
    # pollution_df = get_gios_pollution_data()

    arcgis_handler = ArcGISHandler()

    pollution_map = arcgis_handler.get_pollution_map()
    pollution_data_feature = arcgis_handler.get_pollution_data_feature()

    # response = post_station_data_to_arcgis_online(pollution_df, FEATURE_SERVICE_URL, token)
    print("Script executed successfully")

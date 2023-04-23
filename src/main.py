from arcgis import GIS

from arcgis import GIS
from config import USERNAME, PASSWORD, CLIENT_SECRET, CLIENT_ID
from steps_definitions import get_gios_pollution_data, generate_oauth_token

if __name__ == "__main__":
    print("Starting to execute script")
    token = generate_oauth_token(CLIENT_ID, CLIENT_SECRET)
    pollution_df = get_gios_pollution_data()




    # response = post_station_data_to_arcgis_online(pollution_df, FEATURE_SERVICE_URL, token)
    print("Script executed successfully")

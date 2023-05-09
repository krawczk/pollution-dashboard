import logging
from datetime import datetime

from ArcGISHandler import ArcGISHandler, update_pollution_data_with_new_feature_set
from gios_steps_definitions import get_gios_pollution_data


if __name__ == "__main__":
    logging.info(f"Starting to execute script - {datetime.now()}")
    pollution_df = get_gios_pollution_data(is_long=True)

    arcgis_handler = ArcGISHandler()

    pollution_map = arcgis_handler.get_pollution_map()
    pollution_data_feature_layer = arcgis_handler.get_pollution_data_feature_layer(is_long=True)
    pollution_dashboard = arcgis_handler.get_pollution_dashboard()

    pollution_data_feature_layer.delete_features(where="1=1")

    update_pollution_data_with_new_feature_set(pollution_df, pollution_data_feature_layer, is_long=True)

    logging.info(f"Finished executing script - {datetime.now()}")

import logging
from datetime import datetime

from ArcGISHandler import ArcGISHandler
from GiosHandler import GiosHandler


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info(f"Starting to execute script - {datetime.now()}")

    # Get GIOS pollution data
    gios_handler = GiosHandler()
    pollution_df = gios_handler.get_pollution_data(is_long=True)

    # Handle ArcGIS operations
    arcgis_handler = ArcGISHandler()

    pollution_map = arcgis_handler.get_pollution_map()
    pollution_data_feature_layer = arcgis_handler.get_pollution_data_feature_layer(is_long=True)
    pollution_dashboard = arcgis_handler.get_pollution_dashboard()

    # Delete all existing pollution data
    arcgis_handler.delete_all_pollution_data(is_long=True)

    # Add new pollution data
    arcgis_handler.add_pollution_data(pollution_df, is_long=True)

    logging.info(f"Finished executing script - {datetime.now()}")


if __name__ == "__main__":
    main()

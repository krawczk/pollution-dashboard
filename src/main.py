import logging
from datetime import datetime

from ArcGISHandler import ArcGISHandler
from GiosHandler import GiosHandler


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='logs/app.log')
    logging.info(f"Starting to execute script - {datetime.now()}")

    # Get GIOS pollution data
    gios_handler = GiosHandler()
    pollution_df = gios_handler.get_pollution_data(is_long=True)

    # Handle ArcGIS operations
    arcgis_handler = ArcGISHandler()

    # Delete all existing pollution data
    arcgis_handler.delete_all_pollution_data(is_long=True)

    # Add new pollution data
    arcgis_handler.add_pollution_data(pollution_df, is_long=True)

    logging.info(f"Finished executing script - {datetime.now()}")


if __name__ == "__main__":
    main()

from arcgis import GIS
from config import USERNAME, PASSWORD


def get_pollution_map():
    gis = GIS("https://www.arcgis.com", username=USERNAME, password=PASSWORD)

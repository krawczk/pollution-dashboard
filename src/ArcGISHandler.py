from arcgis import GIS

from config import USERNAME, PASSWORD, POLLUTION_MAP_ID, POLLUTION_DATA_ID


class ArcGISHandler:
    gis = GIS("https://www.arcgis.com", username=USERNAME, password=PASSWORD)

    def __init__(self):
        pass

    def get_pollution_data_feature(self):
        pollution_data = self.gis.content.get(POLLUTION_DATA_ID)
        assert pollution_data.title == "Pollution Data"
        assert pollution_data.owner == "krawczyk_agh_ust"
        return pollution_data

    def get_pollution_map(self):
        pollution_map = self.gis.content.get(POLLUTION_MAP_ID)
        assert pollution_map.title == "Pollution Map"
        assert pollution_map.owner == "krawczyk_agh_ust"
        return pollution_map

    def update_pollution_data_feature(self, pollution_df):
        pass

    def post_station_data_to_arcgis_online(df: pd.DataFrame, feature_service_url: str, token: str) -> Union[dict, str]:
        features = []
        # Iterate over the rows in the dataframe
        for index, row in df.iterrows():
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

            # Send a POST request to the feature service to add a new feature
            features.append({
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

        data = {
            "f": "json",
            "token": token,
            "features": json.dumps(features)
        }
        response = requests.post(feature_service_url + "/addFeatures", data=data)
        # Check the status code of the response to make sure the request was successful
        if response.status_code == 200:
            return response.json()
        else:
            return f"Error adding feature: {response.status_code} {response.reason}"

    def _delete_all_features(feature_service_url: str, token: str) -> Union[dict, str]:
        # Set the parameters for the query operation
        params = {
            "where": "1=1",  # This will return all features
            "returnIdsOnly": True,  # We only need the object IDs of the features
            "f": "json",  # Set the response format to JSON,
            "token": token
        }
        headers = {
            "Content-Type": "application/json",
        }
        # Send a GET request to the query operation
        response = requests.get(feature_service_url + "/query", params=params, headers=headers)
        # Check the status code of the response to make sure the request was successful
        if response.status_code == 200:
            # Get the object IDs of the features from the response
            object_ids = response.json()["objectIds"]
            # If there are no features, return a message
            if len(object_ids) == 0:
                return "There are no features to delete."
            # Set the chunk size
            chunk_size = int(len(object_ids) / 10)
            # Iterate over the object IDs in chunks
            for i in range(0, len(object_ids), chunk_size):
                # Get the current chunk of object IDs
                object_ids_chunk = object_ids[i:i + chunk_size]
                # Set the parameters for the deleteFeatures operation
                params = {
                    "objectIds": ",".join(str(x) for x in object_ids_chunk),  # Convert the object IDs to a string
                    "f": "json",  # Set the response format to JSON
                    "token": token
                }
                # Send a POST request to the deleteFeatures operation
                response = requests.post(feature_service_url + "/deleteFeatures", params=params, headers=headers)
                # Check the status code of the response to make sure the request was successful
                if response.status_code != 200:
                    return f"Error when performing a delete operation: {response.status_code} {response.reason}"

    def _get_all_pollution_data(feature_service_url: str) -> Union[dict, str]:
        # Set the query parameters
        params = {
            "where": "POLLUTION_VALUE>0",  # Filter criteria
            "outFields": "*",  # List of fields to include in the response
            "returnGeometry": "true",  # Include geometry in the response
            "f": "json"  # Response format
        }
        # Send a GET request to the feature service
        response = requests.get(feature_service_url + "/query", params=params)
        # Check the status code of the response
        if response.status_code == 200:
            # Print the response data
            return response.json()
        else:
            # Print an error message
            return f"Error retrieving features: {response.status_code} {response.reason}"

    def generate_oauth_token(client_id: str, client_secret: str) -> str:
        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        }
        r = requests.get("https://www.arcgis.com/sharing/rest/oauth2/token", params=params)

        if r.status_code == 200:
            token = r.json()["access_token"]
            return token
        else:
            return r.text

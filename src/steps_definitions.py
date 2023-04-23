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

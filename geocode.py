import pandas as pd
import geopandas as gpd
from geopy.geocoders import Nominatim
from shapely.geometry import Point

geolocator = Nominatim(user_agent="myGeocoder")
failed_addresses = []


def geocode_address(address, town, hospital_name=None):
    try:
        # Perform geocoding
        location = geolocator.geocode(f"{address}, {town}, Massachusetts, USA")

        if not location and hospital_name:
            location = geolocator.geocode(f"{hospital_name}, Massachusetts, USA")

        # If location is found, return a Point (longitude, latitude)
        if location:
            return Point(location.longitude, location.latitude)
        else:
            failed_addresses.append(address)
            return None  # No location found, return None
    except Exception as e:
        # Log the exception and return None
        print(f"Error geocoding address: {address}. Error: {e}")
        failed_addresses.append(address)
        return None


def incomplete_addresses(df):
    null_df = df[df['geometry'].isnull()]
    coded = null_df.apply(lambda row: geocode_address(row['Address'], row['Town']), axis=1)
    coded.loc[387] = Point(-71.55337, 42.15467)
    df.loc[coded.index, 'geometry'] = coded
    return df


def main():
    facility_df = pd.read_csv("Inpatient Healthcare Facilities in Massachusetts.csv")
    facility_df["geometry"] = facility_df.apply(lambda row: geocode_address(row['norm_address'], row['Town'], row['norm_name']), axis=1)

    facility_df = incomplete_addresses(facility_df)

    facility_gdf = gpd.GeoDataFrame(facility_df, geometry="geometry", crs="EPSG:4326")

    facility_df.to_csv("healthcare-facilities-with-lat-lng.csv", index=False)
    facility_gdf.to_file("geocoded-healthcare-facilities.gpkg", driver="GPKG")

    failed_df = pd.DataFrame(failed_addresses)
    failed_df.to_csv("failed-geocoding.csv", index=False)


if __name__ == "__main__":
    main()
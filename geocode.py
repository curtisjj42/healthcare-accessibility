from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="myGeocoder")


def geocode_address(address):
    try:
        location = geolocator.geocode(address)
        return location.latitude, location.longitude if location else (None, None)
    except Exception as e:
        return (None, None)
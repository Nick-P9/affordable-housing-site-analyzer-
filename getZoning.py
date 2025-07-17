import requests
import backoff
from ratelimit import limits, RateLimitException

# Define the wait strategy for backoff
@backoff.on_exception(backoff.expo, RateLimitException, max_tries=8)
@limits(calls=1, period=1)  # Adjust based on your rate limit
def get_lat_lon_osm(address):
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }
    headers = {
        'User-Agent': 'YourAppName/1.0'  # Replace with your application name and version
    }
    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code == 200:
        results = response.json()
        if results:
            lat = float(results[0]["lat"])
            lon = float(results[0]["lon"])
            osm_link = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=15/{lat}/{lon}"
            return lat, lon, osm_link
        else:
            print("No results found for the address.")
            return None, None, None
    else:
        print(f"Error: {response.status_code}")
        return None, None, None

def query_zoning(lat, lon):
    query_url = "https://bcgishub.broward.org/server/rest/services/GeoHubDownloads/Broward_County_Future_Land_Use/MapServer/0/query"
    params = {
        "geometry": f"{lon},{lat}",  # Note the order: longitude, latitude
        "geometryType": "esriGeometryPoint",
        "inSR": "4326",  # Spatial reference (WGS84)
        "outFields": "*",  # Retrieve all fields
        "f": "json"       # Response format
    }

    # Make the GET request
    response = requests.get(query_url, params=params)
    zoning_data = response.json()

    return zoning_data

def main(address):
    # Get coordinates from the address
    lat, lon, osm_link = get_lat_lon_osm(address)

    if lat and lon:
        print(f"Coordinates: Latitude {lat}, Longitude {lon}")
        print(f"OSM Link: {osm_link}")

        # Query zoning information
        zoning_info = query_zoning(lat, lon)
        
        if 'features' in zoning_info and len(zoning_info['features']) > 0:
            # Extract the first feature
            feature = zoning_info['features'][0]
            attributes = feature['attributes']
            # Extract zoning information based on known field names
            zoning_type = attributes.get('SLUC1', 'Unknown')
            print(f"Zoning Type: {zoning_type}")
        else:
            print("No zoning information found for the given coordinates.")
    else:
        print("Failed to retrieve coordinates.")

# Example usage
address = "FAIRWAY DR, DEERFIELD BEACH, 33441"
main(address)

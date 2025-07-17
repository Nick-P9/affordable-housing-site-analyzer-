import pandas as pd
import requests
import math
import re

# Rate limit and retry configurations
RATE_LIMIT = 1  # Adjust according to API constraints

class RateLimitException(Exception):
    pass


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

def add_suffix_to_number(address):
    suffixes = ['ST', 'AVE', 'CT', 'RD', 'BLVD', 'DR', 'TER', 'CIR']
    
    def replace_suffix(match):
        number = match.group(1)
        suffix = match.group(2).strip().upper()
        if suffix in suffixes:
            if 10 <= int(number) % 100 <= 20:
                ordinal = f"{number}th"
            else:
                ordinal = f"{number}{'st' if number[-1] == '1' else 'nd' if number[-1] == '2' else 'rd' if number[-1] == '3' else 'th'}"
            return ordinal + ' ' + suffix
        else:
            return number + ' ' + suffix

    pattern = r'(\d+)\s*([A-Z]+)'
    return re.sub(pattern, replace_suffix, address)

def clean_address(address):
    address = address.replace(" 1st", "")
    return address.strip()

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of Earth in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c * 0.621371  # Convert to miles
    return distance

def find_schools(lat, lng, radius=5000):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["amenity"="school"](around:{radius},{lat},{lng});
    );
    out body;
    """
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()
    schools = [{'id': element['id'], 'lat': element['lat'], 'lng': element['lon'], 'type': element['tags'].get('amenity', 'school')} for element in data['elements']]
    return schools

def find_grocery_stores(lat, lng, radius=5000):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["shop"="supermarket"](around:{radius},{lat},{lng});
      node["shop"="grocery"](around:{radius},{lat},{lng});
    );
    out body;
    """
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()
    stores = [{'id': element['id'], 'lat': element['lat'], 'lng': element['lon'], 'type': element['tags'].get('shop', 'grocery')} for element in data['elements']]
    return stores

def find_transit_locations(lat, lng, radius=5000):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["public_transport"="stop_position"](around:{radius},{lat},{lng});
      node["highway"="bus_stop"](around:{radius},{lat},{lng});
      node["railway"="station"](around:{radius},{lat},{lng});
      node["railway"="tram_stop"](around:{radius},{lat},{lng});
      node["amenity"="bus_station"](around:{radius},{lat},{lng});
      node["public_transport"="platform"](around:{radius},{lat},{lng});
      node["public_transport"="stop_area"](around:{radius},{lat},{lng});
    );
    out body;
    """
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()
    locations = [{'id': element['id'], 'lat': element['lat'], 'lng': element['lon'], 'type': element['tags'].get('public_transport', element['tags'].get('highway', element['tags'].get('railway', element['tags'].get('amenity', 'transit'))))} for element in data['elements']]
    return locations

def find_medical_facilities(lat, lng, radius=5000):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:{radius},{lat},{lng});
      node["amenity"="clinic"](around:{radius},{lat},{lng});
      node["amenity"="doctors"](around:{radius},{lat},{lng});
    );
    out body;
    """
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()
    facilities = [{'id': element['id'], 'lat': element['lat'], 'lng': element['lon'], 'type': element['tags'].get('amenity', 'medical_facility')} for element in data['elements']]
    return facilities

def transit_points(distance):
    if distance <= 2:
        return 1
    else:
        return 0

def community_points(distance):
    if distance <= 2:
        return 1
    else:
        return 0

def calculate_points(lat, lon):
    schools = find_schools(lat, lon)
    grocery_stores = find_grocery_stores(lat, lon)
    transit_locations = find_transit_locations(lat, lon)
    medical_facilities = find_medical_facilities(lat, lon)

    total_points = 0
    transit_points_total = 0
    community_points_total = 0
    gross_transit_points = 0
    gross_community_points = 0

    # Calculate transit points
    for location in transit_locations:
        distance = calculate_distance(lat, lon, location['lat'], location['lng'])
        points = transit_points(distance)
        gross_transit_points += points
        transit_points_total += points

    # Calculate community service points
    community_services = schools + grocery_stores + medical_facilities
    for service in community_services:
        distance = calculate_distance(lat, lon, service['lat'], service['lng'])
        points = community_points(distance)
        gross_community_points += points
        community_points_total += points

    total_points = transit_points_total + community_points_total

    return {
        "GROSS_TRANSIT_POINTS": gross_transit_points,
        "GROSS_COMMUNITY_POINTS": gross_community_points,
        "Total": total_points
    }

def process_addresses(input_path, output_path):
    df = pd.read_csv(input_path)
    
    # Initialize new columns
    df['LATITUDE'] = None
    df['LONGITUDE'] = None
    df['OSM_ADDRESS_LINK'] = None
    df['GROSS_TRANSIT_POINTS'] = 0.0
    df['GROSS_COMMUNITY_POINTS'] = 0.0

    for index, row in df.iterrows():
        address = clean_address(f"{row['OWN_ADDR1']} {row['OWN_CITY']} {row['OWN_STATE']} {row['OWN_ZIPCD']}")
        formatted_address = add_suffix_to_number(address)
        
        lat, lon, osm_link = get_lat_lon_osm(formatted_address)
        
        df.at[index, 'LATITUDE'] = lat
        df.at[index, 'LONGITUDE'] = lon
        df.at[index, 'OSM_ADDRESS_LINK'] = osm_link
        
        if lat is not None and lon is not None:
            points = calculate_points(lat, lon)
            df.at[index, 'GROSS_TRANSIT_POINTS'] = points['GROSS_TRANSIT_POINTS']
            df.at[index, 'GROSS_COMMUNITY_POINTS'] = points['GROSS_COMMUNITY_POINTS']

    required_columns = [
        'OBJECTID', 'CO_NO', 'PARCEL_ID', 'FILE_T', 'ASMNT_YR', 'BAS_STRT',
        'ATV_STRT', 'DOR_UC', 'LND_VAL', 'ACT_YR_BLT', 'SALE_PRC1', 'SALE_YR1',
        'OWN_NAME', 'OWN_ADDR1', 'OWN_CITY', 'OWN_STATE', 'OWN_ZIPCD', 'PHY_ADDR1',
        'PHY_CITY', 'PHY_ZIPCD', 'Acres', 'LATITUDE', 'LONGITUDE',
        'GROSS_TRANSIT_POINTS', 'GROSS_COMMUNITY_POINTS'
    ]
    
    output_df = df[required_columns]
    output_df.to_csv(output_path, index=False)

if __name__ == "__main__":
    input_path = 'osceola.csv'
    output_path = 'Osceola59Points.csv'
    process_addresses(input_path, output_path)

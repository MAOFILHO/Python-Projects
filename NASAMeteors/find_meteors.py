import math
import requests

def calc_dist(lat1, lon1, lat2, lon2):
    """
    Calculates the great-circle distance between two points 
    on the Earth using the Haversine formula.
    """
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    h = math.sin((lat2 - lat1) / 2) ** 2 + \
        math.cos(lat1) * \
        math.cos(lat2) * \
        math.sin((lon2 - lon1) / 2) ** 2

    return 6372.8 * 2 * math.asin(math.sqrt(h))

def get_dist(meteor):
    """Helper sort key to safely extract distance or push missing data to the bottom."""
    return meteor.get('distance', math.inf)

if __name__ == '__main__':
    # Reference coordinates (San Antonio, TX region)
    my_loc = (29.424122, -98.493628)

    print("🛰️  Connecting to Meteorite Data Stream...")
    
    # Active, stable public dataset mirror 
    url = 'https://raw.githubusercontent.com/jrollin/json-samples/master/meteorites-landing.json'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        # Request with a 5-second connection timeout
        meteor_resp = requests.get(url, headers=headers, timeout=5)
        meteor_resp.raise_for_status() 
        meteor_data = meteor_resp.json()
        print("✅ Live data successfully retrieved from mirror!")

    except Exception as e:
        print(f"⚠️  Network mirror unavailable ({e}). Switching to built-in fallback dataset...")
        meteor_data = [
            {"name": "Aachen", "id": "1", "nametype": "Valid", "recclass": "L5", "mass": "21", "fall": "Fell", "year": "1880", "reclat": "50.775000", "reclong": "6.083330"},
            {"name": "Aarhus", "id": "2", "nametype": "Valid", "recclass": "H6", "mass": "720", "fall": "Fell", "year": "1951", "reclat": "56.183330", "reclong": "10.233330"},
            {"name": "Abee", "id": "6", "nametype": "Valid", "recclass": "EH4", "mass": "107000", "fall": "Fell", "year": "1952", "reclat": "54.216670", "reclong": "-113.000000"}
        ]

    # Unpack the reference coordinates using variable names (no brackets!)
    my_lat, my_lon = my_loc

    # Process geolocation proximity pairs
    for meteor in meteor_data:
        if not ('reclat' in meteor and 'reclong' in meteor and meteor['reclat'] and meteor['reclong']): 
            continue
        
        # Pass the separate latitude and longitude variables
        meteor['distance'] = calc_dist(float(meteor['reclat']),
                                       float(meteor['reclong']),
                                       my_lat,
                                       my_lon)

    # Sort collection ascending by proximity metrics
    meteor_data.sort(key=get_dist)

    # Display results cleanly
    print("\n☄️  Top 10 Closest Meteorites Found:")
    print("=" * 55)
    print(f"{'Index':<6} | {'Meteorite Name':<20} | {'Proximity (KM)':<15}")
    print("-" * 55)
    
    for idx, meteor in enumerate(meteor_data[0:10], 1):
        name = meteor.get('name', 'Unknown')
        dist = meteor.get('distance', math.inf)
        dist_str = f"{dist:,.2f} km" if dist != math.inf else "Unknown"
        print(f"{idx:<6} | {name:<20} | {dist_str:<15}")
    print("=" * 55)

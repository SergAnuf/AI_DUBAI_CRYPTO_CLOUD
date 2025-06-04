import pandas as pd
from tqdm import tqdm
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
import os 
from dotenv import load_dotenv

# Initialize tqdm for pandas
tqdm.pandas()
load_dotenv()


# Define geocoding function
def get_lat_long(address):
    try:
        geolocator = Nominatim(user_agent="unique_app_name_123", timeout=10)
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None  # Ensure consistent tuple return
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"Geocoding error: {e}")
        return None, None



def safe_get_lat_long(address):
    # Example usage with DataFrame:
    # Extract latitude and longitude from the "displayAddress" column
    # and assign them to new columns "latitude" and "longitude"
    # data[["latitude", "longitude"]] = data["displayAddress"].progress_apply(
    #     lambda x: pd.Series(safe_get_lat_long(x))
    # )
    if pd.isnull(address):
        return None, None
    try:
        lat_lon = get_lat_long(address)
        time.sleep(1)  # Respect rate limit
        return lat_lon if lat_lon else (None, None)
    except Exception as e:
        print(f"Error for address '{address}': {e}")
        return None, None


    
def generate_google_maps_html(input_data, api_key=os.getenv("GOOGLE_API_KEY")):
    
    locations = pd.DataFrame(input_data)
    if locations.empty:
        return "<html><body><h1>No locations provided</h1></body></html>"
    
    markers_js = "\n".join([
        f"""
        var marker_{i} = new google.maps.Marker({{
            position: {{ lat: {row['latitude']}, lng: {row['longitude']} }},
            map: map
        }});

        var infowindow_{i} = new google.maps.InfoWindow({{
            content: `<div style="font-size: 16px; font-weight: bold;">{row['title']}</div>`
        }});

        marker_{i}.addListener('click', function() {{
            infowindow_{i}.open(map, marker_{i});
        }});
        """
        for i, row in locations.iterrows()
    ])

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Properties Map</title>
        <style>
            body, html {{ height: 100%; margin: 0; padding: 0; font-family: Arial, sans-serif; }}
            #map {{ height: 100%; width: 100%; }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
          function initMap() {{
            var map = new google.maps.Map(document.getElementById('map'), {{
              zoom: 13,
              center: {{ lat: {locations['latitude'].mean()}, lng: {locations['longitude'].mean()} }}
            }});
            {markers_js}
          }}
        </script>
        <script src="https://maps.googleapis.com/maps/api/js?key={api_key}&callback=initMap" async defer></script>
    </body>
    </html>
    """
    return html




# import os
# import time
# import googlemaps
# import pandas as pd
# from time import sleep
# from functools import lru_cache

# # Initialize Google Maps client
# gmaps = googlemaps.Client(key=os.getenv("GOOGLE_API_KEY"))

# # Safe, rate-limited reverse geocode with retry
# @lru_cache(maxsize=10000)
# def cached_reverse_geocode(lat: float, lng: float, retries=3, delay=0.5) -> dict:
#     for attempt in range(retries):
#         try:
#             sleep(0.15)  # Respect Google's ~10 req/sec limit
#             result = gmaps.reverse_geocode((lat, lng))
#             return result[0] if result else None
#         except Exception as e:
#             if attempt < retries - 1:
#                 time.sleep(delay)
#             else:
#                 print(f"Geocoding failed after {retries} attempts for ({lat}, {lng}): {e}")
#                 return None

# # Parse the API response into useful fields
# def parse_gmaps_response(response: dict) -> dict:
#     if not response or 'address_components' not in response:
#         return {
#             'building_name': None,
#             'street_name': None,
#             'community_name': None,
#             'emirate': None,
#             'full_address': None
#         }

#     components = response['address_components']
    
#     def get_component_by_type(target_type):
#         for comp in components:
#             if target_type in comp['types']:
#                 return comp['long_name']
#         return None

#     return {
#         'building_name': get_component_by_type('premise') or get_component_by_type('plus_code') or get_component_by_type('establishment'),
#         'street_name': get_component_by_type('route'),
#         'community_name': get_component_by_type('sublocality') or get_component_by_type('neighborhood'),
#         'emirate': get_component_by_type('administrative_area_level_1'),
#         'full_address': response.get('formatted_address', '')
#     }


# # Apply function for a row of the DataFrame
# def enrich_with_gmaps(row):
#     try:
#         response = cached_reverse_geocode(row['latitude'], row['longitude'])
#         parsed = parse_gmaps_response(response)
#     except Exception as e:
#         print(f"Row failed at ({row['latitude']}, {row['longitude']}): {e}")
#         parsed = {
#             'building_name': None,
#             'street_name': None,
#             'community_name': None,
#             'emirate': None,
#             'full_address': None
#         }
#     return pd.Series(parsed)

# # Apply to your DataFrame
# df[['building_name', 'street_name', 'community_name', 'emirate', 'full_address']] = (
#     df.apply(enrich_with_gmaps, axis=1)
# )


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

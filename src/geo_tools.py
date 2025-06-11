import pandas as pd
from tqdm import tqdm
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
import os
from dotenv import load_dotenv

# Initialize tqdm for pandas to enable progress bars for DataFrame operations
tqdm.pandas()

# Load environment variables from a .env file
load_dotenv()


def get_lat_long(address):
    """
    Retrieves the latitude and longitude for a given address using the Nominatim geocoding service.

    Args:
        address (str): The address to geocode.

    Returns: tuple: A tuple containing the latitude and longitude as floats, or (None, None) if the address could not
    be geocoded.
    """
    try:
        # Initialize the Nominatim geolocator with a user agent and timeout
        geolocator = Nominatim(user_agent="unique_app_name_123", timeout=10)
        # Perform geocoding to get the location
        location = geolocator.geocode(address)
        if location:
            # Return latitude and longitude if the location is found
            return location.latitude, location.longitude
        else:
            # Return None for both values if the location is not found
            return None, None
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        # Handle geocoding errors and print the error message
        print(f"Geocoding error: {e}")
        return None, None


def safe_get_lat_long(address):
    """
    Safely retrieves the latitude and longitude for a given address, handling null values and rate limits.

    Args:
        address (str): The address to geocode.

    Returns: tuple: A tuple containing the latitude and longitude as floats, or (None, None) if the address could not
    be geocoded.
    """
    # Check if the address is null and return None for both values if so
    if pd.isnull(address):
        return None, None
    try:
        # Call the get_lat_long function to retrieve latitude and longitude
        lat_lon = get_lat_long(address)
        # Respect rate limits by adding a delay
        time.sleep(1)
        # Return the retrieved values or (None, None) if no values are found
        return lat_lon if lat_lon else (None, None)
    except Exception as e:
        # Handle any unexpected errors and print the error message
        print(f"Error for address '{address}': {e}")
        return None, None


def generate_google_maps_html(input_data, api_key=os.getenv("GOOGLE_API_KEY")):
    """
    Generates an HTML page with a Google Maps visualization of the provided locations.

    Args: input_data (list of dict): A list of dictionaries containing location data with keys "latitude",
    "longitude", and "title". api_key (str): The Google Maps API key. Defaults to the value of the "GOOGLE_API_KEY"
    environment variable.

    Returns:
        str: An HTML string containing the Google Maps visualization.
    """
    # Convert the input data into a pandas DataFrame
    locations = pd.DataFrame(input_data)
    if locations.empty:
        # Return a simple HTML message if no locations are provided
        return "<html><body><h1>No locations provided</h1></body></html>"

    # Generate JavaScript code for markers and info windows
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

    # Generate the complete HTML for the map
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
    # Return the generated HTML string
    return html

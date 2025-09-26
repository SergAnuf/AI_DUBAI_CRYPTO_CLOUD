import pandas as pd
from tqdm import tqdm
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
import os
from dotenv import load_dotenv
import ast
import pandasai as pai

# Initialize tqdm for pandas to enable progress bars for DataFrame operations
tqdm.pandas()

# Load environment variables from a .env file
load_dotenv()

# Load PandasAI dataset once at module level
df_ai = pai.load("new-bot/rental-data-london2")


def generate_google_maps_html(input_data, api_key=os.getenv("GOOGLE_API_KEY")):
    """
    #     Generates an HTML page with a Google Maps visualization of the provided locations.
    #
    #     Args:
    #         input_data (list of dict): A list of dictionaries containing location data with keys:
    #                                    "latitude", "longitude", "title", "price_gbp", "property_features".
    #         api_key (str): The Google Maps API key. Defaults to the value of the "GOOGLE_API_KEY"
    #                        environment variable.
    #
    #     Returns:
    #         str: An HTML string containing the Google Maps visualization.
    #     """

    # Convert input data into a DataFrame
    locations = pd.DataFrame(input_data)
    print(type(input_data))
    # Case 1: no rows at all
    if locations.empty:
        return "<html><body><h1>No locations provided</h1></body></html>"

    # Case 2: no ids passed
    if "id" not in locations.columns:
        return "<html><body><h1>No valid IDs provided</h1></body></html>"

    fixed_cols = [
        "id", "latitude", "longitude", "title",
        "price_gbp", "pricing_index", "property_features"
    ]

    # data to display on map (only those with ids in locations)
    selected = df_ai[df_ai["id"].isin(locations["id"])][fixed_cols]

    if selected.empty:
        return "<html><body><h1>No locations to display</h1></body></html>"

    markers_js = []
    for i, row in selected.iterrows():
        feats = row.get("property_features", [])
        if isinstance(feats, str):
            try:
                feats = ast.literal_eval(feats)
            except Exception:
                feats = [feats]
        if not isinstance(feats, list):
            feats = [str(feats)]
        feats = [str(f).strip() for f in feats if f]
        feats_html = "".join(f"<li>{f}</li>" for f in feats)

        markers_js.append(f"""
        var m{i} = new google.maps.Marker({{
            position: {{ lat: {row['latitude']}, lng: {row['longitude']} }},
            map: map
        }});
        var iw{i} = new google.maps.InfoWindow({{
            content: `
                <div style="font-size:14px;max-width:260px;">
                    <div style="font-weight:bold;margin-bottom:6px;">£{row['price_gbp']:,.0f}</div>
                    <div style="margin-bottom:6px;">{row['title']}</div>
                    <div style="font-size:12px;color:#555;margin-bottom:6px;">
                        Pricing index: {row['pricing_index']:.2f}
                    </div>
                    <ul style="margin:0;padding-left:18px;font-size:13px;">
                        {feats_html}
                    </ul>
                </div>`
        }});
        m{i}.addListener('click', () => iw{i}.open(map, m{i}));
        """)

    lat_c = selected["latitude"].mean()
    lng_c = selected["longitude"].mean()

    return f"""
    <html><head><meta charset="utf-8"><title>Properties Map</title>
    <style>body,html{{height:100%;margin:0}}#map{{height:100%;width:100%}}</style>
    </head><body><div id="map"></div>
    <script>
      function initMap() {{
        var map = new google.maps.Map(document.getElementById('map'), {{
          zoom: 13,
          center: {{ lat: {lat_c}, lng: {lng_c} }}
        }});
        {"".join(markers_js)}
      }}
    </script>
    <script src="https://maps.googleapis.com/maps/api/js?key={api_key}&callback=initMap&language=en" async defer></script>
    </body></html>
    """


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

# def generate_google_maps_html(input_data, api_key=os.getenv("GOOGLE_API_KEY")):
#     """
#     Generates an HTML page with a Google Maps visualization of the provided locations.
#
#     Args:
#         input_data (list of dict): A list of dictionaries containing location data with keys:
#                                    "latitude", "longitude", "title", "price_gbp", "property_features".
#         api_key (str): The Google Maps API key. Defaults to the value of the "GOOGLE_API_KEY"
#                        environment variable.
#
#     Returns:
#         str: An HTML string containing the Google Maps visualization.
#     """
#     # Convert input data into a DataFrame
#     locations = pd.DataFrame(input_data)
#     if locations.empty:
#         return "<html><body><h1>No locations provided</h1></body></html>"
#
#     # Generate markers + info windows
#     markers_js = []
#     for i, row in locations.iterrows():
#         # --- Clean property features ---
#         features = row["property_features"]
#
#         if isinstance(features, str):
#             # Try to parse stringified list safely
#             try:
#                 features = ast.literal_eval(features)
#             except Exception:
#                 features = [features]
#         if not isinstance(features, list):
#             features = [str(features)]
#
#         # Clean whitespace/newlines
#         features = [str(f).strip() for f in features if f]
#
#         # Build features HTML list
#         features_html = "".join(f"<li>{feat}</li>" for feat in features)
#
#         markers_js.append(f"""
#         var marker_{i} = new google.maps.Marker({{
#             position: {{ lat: {row['latitude']}, lng: {row['longitude']} }},
#             map: map
#         }});
#
#         var infowindow_{i} = new google.maps.InfoWindow({{
#             content: `
#                 <div style="font-size: 14px; max-width: 260px;">
#                     <div style="font-size: 16px; font-weight: bold; margin-bottom: 6px;">
#                         £{row['price_gbp']:,.0f}
#                     </div>
#                     <div style="margin-bottom: 6px;">
#                         {row['title']}
#                     </div>
#                     <ul style="margin: 0; padding-left: 18px; font-size: 13px;">
#                         {features_html}
#                     </ul>
#                 </div>
#             `
#         }});
#
#         marker_{i}.addListener('click', function() {{
#             infowindow_{i}.open(map, marker_{i});
#         }});
#         """)
#
#     markers_js = "\n".join(markers_js)
#
#     # Generate HTML
#     html = f"""
#     <html>
#     <head>
#         <meta charset="utf-8">
#         <title>Properties Map</title>
#         <style>
#             body, html {{ height: 100%; margin: 0; padding: 0; font-family: Arial, sans-serif; }}
#             #map {{ height: 100%; width: 100%; }}
#         </style>
#     </head>
#     <body>
#         <div id="map"></div>
#         <script>
#           function initMap() {{
#             var map = new google.maps.Map(document.getElementById('map'), {{
#               zoom: 13,
#               center: {{ lat: {locations['latitude'].mean()}, lng: {locations['longitude'].mean()} }}
#             }});
#             {markers_js}
#           }}
#         </script>
#         <script src="https://maps.googleapis.com/maps/api/js?key={api_key}&callback=initMap" async defer></script>
#     </body>
#     </html>
#     """
#     return html

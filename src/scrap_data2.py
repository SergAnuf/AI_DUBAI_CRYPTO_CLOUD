import requests
import json
import os
from typing import List, Dict, Any
import re
import asyncio
import nest_asyncio

from scrapfly import ScrapflyClient, ScrapeConfig
from dotenv import load_dotenv
from src.constants import FURNISH_TYPES,FURNISH_TYPES_EXCEPTION,LETTING_TYPES,LETTING_TYPES_EXCEPTION,PROPERTY_TYPES,PROPERTY_TYPES_EXCEPTION



API_URL = "https://servisgas-pricing.hf.space/explain"

load_dotenv()

# Initialize Scrapfly client
scrapfly = ScrapflyClient(key=os.getenv("SCRAPFLY_API_KEY"))



def detect_rightmove_links(query: str):
    """ Detect any Rightmove property URLs within a text string. Returns a list of cleaned RightMove URLs if found, otherwise [] """
    # Remove fragments like #/?channel=RES_LET or #... after each URL
    cleaned_query = re.sub(r"#.*?(?=\s|,|$)", "", query.strip())
    # Regex to match Rightmove property URLs
    pattern = r"https?://(?:www\.)?rightmove\.co\.uk/properties/\d+"
    # Find all URLs in text
    matches = re.findall(pattern, cleaned_query)
    if matches:
       # Deduplicate and return clean list
       unique_links = list(dict.fromkeys(matches))
       return unique_links
    else:
       return []

# -------------------------------------------------------
# JSON MINING — finds *any* JSON block with property data
# -------------------------------------------------------

def mine_json_objects(text: str):
    """Extract every JSON object from text safely."""
    decoder = json.JSONDecoder()
    pos = 0
    length = len(text)

    while pos < length:
        start = text.find("{", pos)
        if start == -1:
            return
        try:
            obj, end = decoder.raw_decode(text[start:])
            yield obj
            pos = start + end
        except:
            pos = start + 1


def extract_property_json(html: str) -> Dict[str, Any]:
    """
    Scans *all* JSON blocks in the HTML and returns
    the one which contains property fields.
    """

    for obj in mine_json_objects(html):
        if not isinstance(obj, dict):
            continue

        # Direct property JSON
        if (
            "id" in obj and
            ("address" in obj or "location" in obj or "prices" in obj)
        ):
            return obj

        # Nested property JSON
        for key, val in obj.items():
            if isinstance(val, dict) and "id" in val:
                return val

    return None


def normalize_category(value, allowed, exception):
    """Return cleaned category if valid, otherwise exception."""
    if not value:
        return exception

    if isinstance(allowed, list):
        return value if value in allowed else exception

    return exception

# -------------------------------------------------------
# ASYNC SCRAPER
# -------------------------------------------------------

async def scrape_properties(urls: List[str]) -> List[Dict[str, Any]]:
    tasks = [
        ScrapeConfig(
            url=url,
            asp=True,
            country="GB",
            render_js=False
        )
        for url in urls
    ]

    results = []

    async for result in scrapfly.concurrent_scrape(tasks):
        html = result.content
        raw_data = extract_property_json(html)
        if raw_data:
            results.append(parse_property(raw_data))

    return results


# -------------------------------------------------------
# SAFE RUNNER
# -------------------------------------------------------

def run_scraper_safe(urls: List[str]):
    try:
        return asyncio.run(scrape_properties(urls))
    except RuntimeError:
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(scrape_properties(urls))


def parse_property(data: Dict[str, Any]) -> Dict[str, Any]:

    desc = (data.get("text", {}).get("description") or "").lower()
    phrase = (data.get("text", {}).get("propertyPhrase") or "").lower()

    # Correct fields from Rightmove JSON
    lettings = data.get("lettings", {})

    let_raw = lettings.get("letType")
    furn_raw = lettings.get("furnishType")
    deposit_raw = lettings.get("deposit")
    prop_raw = data.get("propertyType")

    bedrooms = data.get("bedrooms")
    bathrooms = data.get("bathrooms")

    latitude = data.get("location", {}).get("latitude")
    longitude = data.get("location", {}).get("longitude")

    # ------------ Fix letType ------------
    if not let_raw:
        let_raw = "Long term" if data.get("prices", {}).get("primaryPrice") else None
    let_type = normalize_category(let_raw, LETTING_TYPES, LETTING_TYPES_EXCEPTION)

    # ------------ Fix furnishType ------------
    if not furn_raw:
        if "furnished" in desc:
            furn_raw = "Furnished"
        elif "unfurnished" in desc:
            furn_raw = "Unfurnished"

    furnish_type = normalize_category(furn_raw, FURNISH_TYPES, FURNISH_TYPES_EXCEPTION)

    # ------------ Fix propertyType ------------
    if not prop_raw:
        if "apartment" in phrase or "apartment" in desc:
            prop_raw = "Apartment"
        elif "flat" in phrase or "flat" in desc:
            prop_raw = "Flat"

    property_type = normalize_category(prop_raw, PROPERTY_TYPES, PROPERTY_TYPES_EXCEPTION)

    return {
        "id": str(data.get("id")),
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "propertyType": property_type,
        "deposit": deposit_raw,
        "letType": let_type,
        "furnishType": furnish_type,
        "latitude": latitude,
        "longitude": longitude,
    }


def to_model_outputs(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert property data to model input format."""
    API_URL = "https://servisgas-pricing.hf.space/explain"

    payload = {"model_params": data}
    response = requests.post(API_URL, json=payload)

    return response.json()



# dictionary_list = run_scraper_safe(["https://www.rightmove.co.uk/properties/169513070#/?channel=RES_LET"])
#
# # Extract the first (and only) property JSON
# print(dictionary_list[0])

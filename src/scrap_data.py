import asyncio
import json
import os
from typing import List, Dict, Any
import re
import random

from scrapfly import ScrapflyClient, ScrapeApiResponse, ScrapeConfig
from dotenv import load_dotenv

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

# ---------------------
# JSON extraction utils
# ---------------------
def find_json_objects(text: str, decoder=json.JSONDecoder()):
    """Find and yield JSON objects embedded in a text blob."""
    pos = 0
    while True:
        start = text.find("{", pos)
        if start == -1:
            break
        try:
            result, index = decoder.raw_decode(text[start:])
            yield result
            pos = start + index
        except ValueError:
            pos = start + 1


def extract_property_json(result: ScrapeApiResponse) -> Dict[str, Any]:
    """Extract Rightmove's PAGE_MODEL JSON block from HTML."""
    script = result.selector.xpath("//script[contains(.,'PAGE_MODEL = ')]/text()").get()
    if not script:
        print(f"⚪ Not a property page: {result.context['url']}")
        return None

    json_candidates = list(find_json_objects(script))
    if not json_candidates:
        print(f"⚪ Could not parse JSON from: {result.context['url']}")
        return None

    data = json_candidates[0]
    return data.get("propertyData")


def parse_property(data: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize the Rightmove property JSON into a cleaner schema."""
    return {
        "id": str(data.get("id")),
        "status": {
            "published": data.get("published", True),
            "archived": data.get("archived", False),
        },
        "text": {
            "description": data.get("text", {}).get("description"),
            "propertyPhrase": data.get("text", {}).get("propertyPhrase"),
            "disclaimer": data.get("text", {}).get("disclaimer"),
            "shortDescription": data.get("text", {}).get("shortDescription"),
            "pageTitle": data.get("text", {}).get("pageTitle"),
        },
        "prices": {
            "primaryPrice": data.get("prices", {}).get("primaryPrice"),
            "secondaryPrice": data.get("prices", {}).get("secondaryPrice"),
            "displayPriceQualifier": data.get("prices", {}).get("displayPriceQualifier"),
        },
        "address": {
            "displayAddress": data.get("address", {}).get("displayAddress"),
            "outcode": data.get("address", {}).get("outcode"),
            "incode": data.get("address", {}).get("incode"),
            "countryCode": data.get("address", {}).get("countryCode"),
            "ukCountry": data.get("address", {}).get("ukCountry"),
        },
        "bedrooms": data.get("bedrooms"),
        "bathrooms": data.get("bathrooms"),
        "propertySubType": data.get("propertySubType"),
        "images": [img.get("srcUrl") for img in data.get("images", []) if img.get("srcUrl")],
        "agent": {
            "name": data.get("customer", {}).get("branchDisplayName"),
            "branch_id": data.get("customer", {}).get("branchId"),
            "telephone": data.get("customer", {}).get("telephone"),
        },
        "url": f"https://www.rightmove.co.uk/properties/{data.get('id')}",
    }

# ---------------------
# Async scraper
# ---------------------

async def scrape_properties(urls: List[str]) -> List[Dict[str, Any]]:
    """Scrape multiple RightMove property pages asynchronously."""
    to_scrape = [
        ScrapeConfig(url=url, asp=True, country="GB", render_js=False)
        for url in urls
    ]
    results = []
    async for result in scrapfly.concurrent_scrape(to_scrape):
        raw_data = extract_property_json(result)
        if raw_data:
            parsed = parse_property(raw_data)
            results.append(parsed)
    return results

# ---------------------
# Test run
# ---------------------

def run_scraper_safe(urls):
    """
    Safely run the async scrape_properties() function from both
    sync and async environments. Returns scraped data.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # Already inside an async loop (e.g. Streamlit or FastAPI)
        # -> schedule and await manually
        future = asyncio.ensure_future(scrape_properties(urls))
        return asyncio.run_coroutine_threadsafe(future, loop).result()
    else:
        # Normal Python script
        return asyncio.run(scrape_properties(urls))


def parse_price_pcm(price_str):
    """
    Convert a price string like '£2,362 pcm' to a numeric monthly value (float).
    Always assumes prices are per calendar month (pcm).
    Returns None if parsing fails.
    """
    if not isinstance(price_str, str):
        return None

    match = re.search(r'[\d,]+(?:\.\d+)?', price_str)
    if not match:
        return None

    return float(match.group().replace(',', ''))



def to_property_dicts(scraped_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert scraped Rightmove property JSON into a list of property dictionaries.

    Returns a list of dicts ready for JSON serialization or DataFrame creation.
    """
    properties = []

    for item in scraped_data:
        address = item.get("address", {}).get("displayAddress")
        bedrooms = item.get("bedrooms")
        price_str = item.get("prices", {}).get("primaryPrice")
        url = item.get("url")

        price = parse_price_pcm(price_str)
        expected_rent = round(price * random.uniform(0.85, 1.15), 1) if price else None

        properties.append({
                "bedrooms": bedrooms,
                "displayAddress": address,
                "Rent (£/pcm)": price,
                "expectedRent (£/pcm)": expected_rent,
                "url": url
            })
    return properties
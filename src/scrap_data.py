import asyncio
import json
import os
from typing import List, Dict, Any

from scrapfly import ScrapflyClient, ScrapeApiResponse, ScrapeConfig
from dotenv import load_dotenv

load_dotenv()

# Initialize Scrapfly client
SCRAPFLY_KEY = os.getenv("SCRAPFLY_API_KEY")
scrapfly = ScrapflyClient(key=SCRAPFLY_KEY)

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
    """Scrape multiple Rightmove property pages asynchronously."""
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

async def run():
    urls = [
        "https://www.rightmove.co.uk/properties/164903663#/?channel=RES_LET",
        "https://www.rightmove.co.uk/properties/167855057#/?channel=RES_LET",
    ]
    data = await scrape_properties(urls)
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(run())


from src.tools import safe_dataframe_tool, create_plotly_code
from src.classifiers import llm_classifier, is_uae_real_estate_query
from src.geo_tools import generate_google_maps_html
from src.scrap_data import run_scraper_safe, detect_rightmove_links,to_property_dicts
import json


def safe_user_query(q: str) -> str:
    """
    Sanitizes a user query by replacing problematic characters with safe alternatives.

    Args:
        q (str): The user query string.

    Returns:
        str: The sanitized query string.
    """
    return q.replace("'", "`").replace("’", "`").replace("‘", "`")


def main_agent(query: str):
    """
    Processes a user query related to London real estate and returns a structured response.

    Args:
        query (str): The user query string.

    Returns:
        dict: A structured response with one of the following formats:
            - type="message": {"type": "message", "message": str}
            - type="data": {"type": "data", "data": list[dict]}
            - type="plot": {"type": "plot", "result": str, "data": list[dict]}
            - type="html": {"type": "html", "content": str}
            - type="error": {"type": "error", "error": str, "solution": Optional[str]}
    """
    # Step 0: If correct RightMoves URLs are provided, trigger the scraper directly.
    urls  = detect_rightmove_links(query)
    print("Detected URLs:", len(urls))
    if len(urls)>0:
        try:
            scraped_data = run_scraper_safe(urls)
            data = to_property_dicts(scraped_data)
            return {"type": "pricing_data", "data": data}
        except:
            return {"type": "message",
                "message": "The model server is busy right now."}

    # Step 1: Relevance QUERY check if no URLs are provided.
    # Determine if the query is relevant to London real estate.
    if not is_uae_real_estate_query(query):
        return {"type": "message",
                "message": "This is an irrelevant question to London property."}

    # Step 2: Sanitize the query and classify the user's intent.
    query = safe_user_query(query)
    action = llm_classifier(query)
    final_input = json.dumps({"query": query, "action": action})

    # Step 3: Fetch data using a safe dataframe tool.
    # The tool processes the query and action to return data in JSON format.
    data_json_str = safe_dataframe_tool.invoke(final_input)
    data_dict = json.loads(data_json_str)

    # Handle errors in the data fetching process.
    if not data_dict.get("success"):
        return {"type": "error",
                "error": data_dict.get("error"),
                "solution": data_dict.get("solution")}

    results = data_dict.get("result", [])

    # Step 4: Normalize results.
    # Ensure results are in a consistent format for further processing.
    if results is None:
        return {"type": "message",
                "message": "No properties found. Please refine your search."}

    if isinstance(results, (int, float, str)):
        results = [{"value": results}]

    if not isinstance(results, (list, tuple)) or len(results) == 0:
        return {"type": "message",
                "message": "No properties found. Please refine your search."}

    # Step 5: Execute the action based on the classified intent.
    if action == "output":
        # Return the data as-is.
        return {"type": "data", "data": results}

    elif action == "plot_stats":
        # Generate a Plotly visualization based on the results.
        viz_input = json.dumps({"data": results, "query": query})
        result_json_str = create_plotly_code.invoke(viz_input)
        result = json.loads(result_json_str)
        return {"type": "plot", "result": result["result"], "data": results}

    elif action == "geospatial_plot":
        # Generate a geospatial plot using Google Maps if the result set is small.
        if len(results) < 50:
            html = generate_google_maps_html(results)
            return {"type": "html", "content": html}
        else:
            return {"type": "message",
                    "message": "Too many properties to display. Please refine your search."}

    else:
        # Handle unknown actions.
        return {"type": "error",
                "error": f"Unknown action '{action}' from classifier."}
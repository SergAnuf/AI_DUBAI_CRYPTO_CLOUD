from src.tools import safe_dataframe_tool, extract_data_intent, create_plotly_code
from src.classifiers import llm_classifier, is_uae_real_estate_query
from src.geo_tools import generate_google_maps_html
import json


def main_agent(query: str):
    """
    Processes a user query related to London real estate and returns a structured response.

    Returns:
        dict: with keys depending on type:
            - type="message": {"type": "message", "message": str}
            - type="data": {"type": "data", "data": list[dict]}
            - type="plot": {"type": "plot", "result": str, "data": list[dict]}
            - type="html": {"type": "html", "content": str}
            - type="error": {"type": "error", "error": str, "solution": Optional[str]}
    """

    # Step 1: Relevance check
    if not is_uae_real_estate_query(query):
        return {"type": "message",
                "message": "This is an irrelevant question to London property."}

    # Step 2: Extract data intent
    data_intent = query
    # data_intent = extract_data_intent.invoke(query)

    # Step 3: Fetch data
    data_json_str = safe_dataframe_tool.invoke(data_intent)
    data_dict = json.loads(data_json_str)

    if not data_dict.get("success"):
        return {"type": "error",
                "error": data_dict.get("error"),
                "solution": data_dict.get("solution")}

    results = data_dict.get("result", [])

    # 🔹 Normalize results
    if results is None:
        return {"type": "message",
                "message": "No properties found. Please refine your search."}

    if isinstance(results, (int, float, str)):
        results = [{"value": results}]

    if not isinstance(results, (list, tuple)) or len(results) == 0:
        return {"type": "message",
                "message": "No properties found. Please refine your search."}

    # Step 5: Classify the user’s goal
    action = llm_classifier(query)

    # Step 6: Execute action
    if action == "output":
        return {"type": "data", "data": results}

    elif action == "plot_stats":
        viz_input = json.dumps({"data": results, "query": query})
        result_json_str = create_plotly_code.invoke(viz_input)
        result = json.loads(result_json_str)
        return {"type": "plot", "result": result["result"], "data": results}

    elif action == "geospatial_plot":
        if len(results) < 50:
            html = generate_google_maps_html(results)
            return {"type": "html", "content": html}
        else:
            return {"type": "message",
                    "message": "Too many properties to display. Please refine your search."}

    else:
        return {"type": "error",
                "error": f"Unknown action '{action}' from classifier."}
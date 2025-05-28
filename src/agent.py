from src.tools import visualize_tool, safe_dataframe_tool
from src.classifiers import llm_classifier, is_uae_real_estate_query
from src.geo_tools import generate_google_maps_html

"Main agent function to handle user queries related to UAE real estate."

def main_agent(query: str):
    if not is_uae_real_estate_query(query):
        return {"type": "output", "data": "This is an irrelevant question to UAE property."}

    data = safe_dataframe_tool(query)
    if isinstance(data, dict) and data.get("error"):
        return data

    action = llm_classifier(query)

    if action == "output":
        return {"type": "data", "data": data}

    elif action == "plot_stats":
        result = visualize_tool.invoke({"data": data, "query": query})
        return {"type": "plot", **result}

    elif action == "geospatial_plot":
        result = generate_google_maps_html(data)
        return {"type": "html","content": result}

    else:
        return {"error": f"Unknown action '{action}' from classifier."}
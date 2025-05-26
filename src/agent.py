from src.tools import visualize_tool, safe_dataframe_tool
from src.classifiers import llm_classifier, is_uae_real_estate_query

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
        return {"error": "Geospatial plotting tool not implemented yet."}

    else:
        return {"error": f"Unknown action '{action}' from classifier."}
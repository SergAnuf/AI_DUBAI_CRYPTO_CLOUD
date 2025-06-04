from src.tools import safe_dataframe_tool, extract_data_intent, create_plotly_code
from src.classifiers import llm_classifier, is_uae_real_estate_query
from src.geo_tools import generate_google_maps_html
import json

"Main agent function to handle user queries related to UAE real estate."


def main_agent(query: str):
    # Step 1: Check if query is relevant
    if not is_uae_real_estate_query(query):
        return {"type": "output", "data": "This is an irrelevant question to UAE property."}

    # Step 2: Extract data intent from user query
    data_intent = extract_data_intent.invoke(query)

    # Step 3: Use PandasAI to retrieve relevant data
    data_json_str = safe_dataframe_tool.invoke(data_intent)
    data_dict = json.loads(data_json_str)

    if not data_dict.get("success"):
        return {"type": "error", "error": data_dict.get("error"), "solution": data_dict.get("solution")}

    # Step 4: Classify the user's goal
    action = llm_classifier(query)
    
    
    # Step 5: Take action based on user intent
    if action == "output":
        return {"type": "data", "data": data_dict["result"]}
    
    
    elif action == "plot_stats":
       
        viz_input = json.dumps({"data": data_dict["result"], "query": query})
        result_json_str = create_plotly_code.invoke(viz_input)
        result = json.loads(result_json_str)
        return {"type": "plot", **result}

    elif action == "geospatial_plot":
        
        html = generate_google_maps_html(data_dict["result"])
        return {"type": "html", "content": html}

    else:
        return {"type": "error", "error": f"Unknown action '{action}' from classifier."}
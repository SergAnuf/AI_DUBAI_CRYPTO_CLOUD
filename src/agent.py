from src.tools import safe_dataframe_tool, extract_data_intent, create_plotly_code
from src.classifiers import llm_classifier, is_uae_real_estate_query
from src.geo_tools import generate_google_maps_html
import json

"""
Main agent function to handle user queries related to UAE real estate.
"""


def main_agent(query: str):
    """
    Processes a user query related to London real estate and returns a structured response.

    Args:
        query (str): The user query to process.

    Returns:
        dict: A dictionary containing the result type and corresponding data or error message.
              Possible keys in the dictionary:
              - "type": The type of result (e.g., "output", "data", "plot", "html", "error").
              - "data": The data or message to display (for "output" or "data" types).
              - "result": The plot code (for "plot" type).
              - "content": The HTML content (for "html" type).
              - "error": The error message (for "error" type).
              - "solution": Suggested solution for the error (optional, for "error" type).
    """
    # Step 1: Check if query is relevant
    if not is_uae_real_estate_query(query):
        return {"type": "output", "data": "This is an irrelevant question to London property."}

    # Step 2: Extract data intent from user query
    data_intent = query
    # data_intent = query  extract_data_intent.invoke(query)
    print("The type of the data needed = ".format(data_intent))

    # Step 3: Use PandasAI to retrieve relevant data
    data_json_str = safe_dataframe_tool.invoke(data_intent)
    data_dict = json.loads(data_json_str)

    # Handle errors in data retrieval
    if not data_dict.get("success"):
        return {"type": "error", "error": data_dict.get("error"), "solution": data_dict.get("solution")}

    # Step 4: Classify the user's goal
    action = llm_classifier(query)
    print("The number of properties found = ".format(len(data_dict["result"])))

    # Step 5: Take action based on user intent
    if action == "output":
        # Return the data as a table
        return {"type": "data", "data": data_dict["result"]}

    elif action == "plot_stats":
        # Generate and return a plot based on the data
        viz_input = json.dumps({"data": data_dict["result"], "query": query})
        result_json_str = create_plotly_code.invoke(viz_input)
        result = json.loads(result_json_str)
        return {
            "type": "plot",
            "result": result["result"],  # the plot code
            "data": data_dict["result"]  # the dataset
        }

    elif action == "geospatial_plot":
        # Generate and return a geospatial plot as HTML
        if data_dict["result"] is None or len(data_dict["result"]) == 0:
            return {"type": "output", "data": "No properties found. Please redefine your search"}
        elif len(data_dict["result"]) < 50:
            html = generate_google_maps_html(data_dict["result"])
            return {"type": "html", "content": html}
        else:
            return {"type": "output", "data": "Too many properties to display. Please refine your search"}

    else:
        # Handle unknown actions
        return {"type": "error", "error": f"Unknown action '{action}' from classifier."}
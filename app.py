import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd
from src.tools import visualize_tool, safe_dataframe_tool
from src.classifiers import llm_classifier, is_uae_real_estate_query

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Set up the page
st.set_page_config(page_title="UAE Real Estate Chat", layout="wide")
st.title("🏠 UAE Real Estate Chat Assistant")
st.write("Ask questions about the UAE real estate market data")

query = st.text_input("Enter your real estate query:")


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


if query:
    with st.spinner("Processing your query..."):
        result = main_agent(query)

    if result.get("error"):
        st.error(result["error"])

    elif result["type"] == "output":
        st.info(result["data"])

    elif result["type"] == "data":
        st.success("Here is the data related to your query:")
        st.dataframe(result["data"])

    elif result["type"] == "plot":
        image_buf = result.get("image_bytes")
        st.image(image_buf, use_column_width=True)
     
    else:
        st.warning("Unexpected result type received.")
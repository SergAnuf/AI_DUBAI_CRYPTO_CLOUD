import streamlit as st
import pandas as pd
from src.agent import main_agent


# Set up the page "HELLO WORLD"
st.set_page_config(page_title="UAE Real Estate Chat", layout="wide")
st.title("🏠 UAE Real Estate Chat Assistant")
st.write("Ask questions about the UAE real estate market data")

query = st.text_input("Enter your real estate query:")


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
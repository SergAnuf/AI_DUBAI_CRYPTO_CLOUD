import streamlit as st
from dotenv import load_dotenv
import os
from data_processing import load_and_preprocess_data
from pandasai_helper import PandasAIAssistant
import pandas as pd

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Set up the page
st.set_page_config(page_title="UAE Real Estate Chat", layout="wide")
st.title("🏠 UAE Real Estate Chat Assistant")
st.write("Ask questions about the UAE real estate market data")

@st.cache_resource
def initialize_assistant():
    """
    Initialize the PandasAI assistant with cached data
    """
    try:
        df = load_and_preprocess_data("data/uae_real_estate_2024.csv")
        return PandasAIAssistant(api_key, df)
    except Exception as e:
        st.error(f"Initialization error: {e}")
        return None

# Initialize assistant
if not api_key:
    st.error("API key not found. Check your .env file and variable name.")
    st.stop()

assistant = initialize_assistant()

if not assistant:
    st.stop()

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask a question about the UAE real estate data"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get assistant response
    with st.spinner("Analyzing data..."):
        response = assistant.chat(prompt)
    print(type(response))
    # Display assistant response
    with st.chat_message("assistant"):
        if isinstance(response, str):
            st.markdown(response)
        elif isinstance(response, pd.DataFrame):
            st.dataframe(response)
        elif hasattr(response, "figure"):  # matplotlib/plotly figures
            st.pyplot(response)
        elif hasattr(response, "__html__"):  # Plotly chart or other embeddable HTML
            st.components.v1.html(response.__html__(), height=600)
        else:
            st.write(response)
    
    # Save assistant response (stringify if necessary)
    response_content = response if isinstance(response, str) else str(response)
    st.session_state.messages.append({"role": "assistant", "content": response_content})

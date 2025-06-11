import streamlit as st
from src.agent import main_agent
import streamlit.components.v1 as components

# Set the page configuration for the Streamlit app
st.set_page_config(page_title="UAE Real Estate Chat", layout="wide")

# UI Elements
# Display the main title of the application
st.markdown("<h1 style='font-size: 70px;'>🏠 UAE Real Estate Chat Assistant</h1>", unsafe_allow_html=True)
# Display a subtitle describing the purpose of the application
st.markdown("<p style='font-size: 50px;'>Ask questions about the UAE real estate market data</p>", unsafe_allow_html=True)

# Query input
# Display a label for the query input field
st.markdown("<label style='font-size:30px;'>Enter your real estate query:</label>", unsafe_allow_html=True)

# Text input field for the user to enter their query
# The label is empty because a custom label is styled above
query = st.text_input(label="", key="real_estate_query")

# Check if the user has entered a query
if query:
    # Display a spinner while processing the query
    with st.spinner("Processing your query..."):
        # Call the main_agent function to process the query
        result = main_agent(query)

    # Handle different types of results returned by main_agent
    if result.get("error"):
        # Display an error message if an error occurred
        st.error(result["error"])

    elif result["type"] == "output":
        # Display informational text if the result is of type "output"
        st.info(result["data"])

    elif result["type"] == "data":
        # Display a success message and render the data as a table
        st.success("Here is the data related to your query:")
        st.dataframe(result["data"])

    elif result["type"] == "plot":
        # Execute and render the plot code if the result is of type "plot"
        plot_code = result.get("result")
        exec(plot_code)

    elif result["type"] == "html":
        # Render HTML content if the result is of type "html"
        html_code = result.get("content")
        components.html(html_code, height=600)

    else:
        # Display a warning if the result type is unexpected
        st.warning("Unexpected result type received.")
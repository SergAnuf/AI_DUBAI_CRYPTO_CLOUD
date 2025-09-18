import streamlit as st
from src.agent import main_agent
import streamlit.components.v1 as components
import pandas as pd
from src.tools import contextualize_query
from collections import deque

# Set the page configuration for the Streamlit app
st.set_page_config(page_title="London Real Estate Chat", layout="wide")

# UI Elements
# Display the main title of the application
st.markdown("<h1 style='font-size: 70px;'>🏠 London Real Estate Chat Assistant</h1>", unsafe_allow_html=True)
# Display a subtitle describing the purpose of the application
st.markdown("<p style='font-size: 50px;'>Ask questions about the London real estate market data</p>", unsafe_allow_html=True)

# Query input
# Display a label for the query input field
st.markdown("<label style='font-size:30px;'>Enter your real estate query:</label>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = deque(maxlen=12)

# Show conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Text input field for the user to enter their query
# The label is empty because a custom label is styled above
query = st.text_input(label="", key="real_estate_query")

# Check if the user has entered a query
if query:
    # Append the user's query to the session state messages
    st.session_state.messages.append({"role": "user", "content": query})
    # 🔹 Step [0]: Contextualize the query (dummy for now)
    final_query = contextualize_query(query, history=st.session_state.messages)

    # Show what will be sent downstream so you can verify integration
    st.caption(f"Contextualized query → {final_query}")
    # Display a spinner while processing the query
    with st.spinner("Processing your query..."):
        # Call the main_agent function to process the query
        result = main_agent(final_query)

    # Handle different types of results returned by main_agent
    if result.get("error"):
        # Display an error message if an error occurred
        st.error(result["error"])
        st.session_state.messages.append({"role": "assistant", "content": result["error"]})

    elif result["type"] == "output":
        # Display informational text if the result is of type "output"
        st.info(result["data"])

    elif result["type"] == "data":
        # Display a success message and render the data as a table
        st.success("Here is the data related to your query:")
        st.dataframe(result["data"])
        st.session_state.messages.append({"role": "assistant", "content": pd.DataFrame(result["data"]).head(3).to_markdown()})

    elif result["type"] == "plot":
        plot_code = result.get("result")
        df = pd.DataFrame(result.get("data"))
        exec_globals = {"pd": pd, "px": __import__("plotly.express"), "st": st, "df": df}
        try:
            exec(plot_code, exec_globals)
            # Take a small sample of the dataframe for history
            if not df.empty:
                df_sample = df.head(3).to_markdown(index=False)  # first 3 rows as Markdown table
            else:
                df_sample = "_no data available_"
            # Append informative history message
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": (
                        f"Generated plot with code:\n```python\n{plot_code}\n```\n"
                        f"Data sample used:\n\n{df_sample}"
                    )
                }
            )
        except Exception as e:
            st.error(f"Plot generation failed: {e}")
            st.session_state.messages.append(
                {"role": "assistant", "content": f"Plot generation failed: {e}"}
            )


    elif result["type"] == "html":
        # Render HTML content if the result is of type "html"
        try:
            html_code = result.get("content")
            components.html(html_code, height=600)
            st.session_state.messages.append({"role": "assistant", "content": "Showed properties on Google Maps"})
        except:
            st.error("Failed to display properties on Google Maps.")

    else:
        # Display a warning if the result type is unexpected
        st.warning("Unexpected result type received.")
        st.session_state.messages.append({"role": "assistant", "content": "Unexpected result type received."})
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from collections import deque

from src.agent import main_agent
from src.tools import contextualize_query


# -------------------
# Streamlit Page Setup
# -------------------
st.set_page_config(page_title="London Real Estate Chat", layout="wide")

st.markdown("<h1 style='font-size: 70px;'>🏠 London Real Estate Chat Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 50px;'>Ask questions about the London real estate market data</p>", unsafe_allow_html=True)
st.markdown("<label style='font-size:30px;'>Enter your real estate query:</label>", unsafe_allow_html=True)


# -------------------
# Session State Setup
# -------------------
if "messages" not in st.session_state:
    st.session_state.messages = deque(maxlen=12)

# -------------------
# Show Conversation History
# -------------------
# Show conversation history
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Only add thumbs to assistant messages
        if msg["role"] == "assistant":
            col1, col2, _ = st.columns([0.1, 0.1, 0.8])  # two small cols, one spacer
            with col1:
                st.button("👍", key=f"up_{i}")
            with col2:
                st.button("👎", key=f"down_{i}")


# Clear conversation
if st.button("🔄 Restart Conversation"):
    st.session_state.messages.clear()
    st.rerun()  # refresh the app

# -------------------
# User Input
# -------------------
query = st.text_input(
    label="Real Estate Query",
    key="real_estate_query",
    label_visibility="collapsed"  # keeps accessibility warnings away
)

# -------------------
# Query Handling
# -------------------
if query:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": query})

    # Contextualize query (LLM could expand later)
    final_query = contextualize_query(query, history=st.session_state.messages)
    st.caption(f"Contextualized query → {final_query}")

    with st.spinner("Processing your query..."):
        result = main_agent(final_query)

    # Unified handling by result type
    result_type = result.get("type")

    if result_type == "error":
        st.error(result["error"])
        st.session_state.messages.append(
            {"role": "assistant", "content": result["error"]}
        )

    elif result_type == "message":
        st.info(result["message"])
        st.session_state.messages.append(
            {"role": "assistant", "content": result["message"]}
        )

    elif result_type == "data":
        st.success("Here is the data related to your query:")
        st.dataframe(result["data"])

        # Add a short sample for history
        df = pd.DataFrame(result["data"])
        df_sample = df.head(3).to_markdown(index=False)
        st.session_state.messages.append(
            {"role": "assistant", "content": f"Returned data sample:\n\n{df_sample}"}
        )

    elif result_type == "plot":
        plot_code = result.get("result")
        df = pd.DataFrame(result.get("data"))
        exec_globals = {"pd": pd, "px": __import__("plotly.express"), "st": st, "df": df}

        try:
            exec(plot_code, exec_globals)
            df_sample = df.head(3).to_markdown(index=False)
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": (
                        f"Generated plot with code:\n```python\n{plot_code}\n```\n"
                        f"Data sample used:\n\n{df_sample}"
                    ),
                }
            )
        except Exception as e:
            st.error(f"Plot generation failed: {e}")
            st.session_state.messages.append(
                {"role": "assistant", "content": f"Plot generation failed: {e}"}
            )

    elif result_type == "html":
        try:
            html_code = result.get("content")
            components.html(html_code, height=600)
            st.session_state.messages.append(
                {"role": "assistant", "content": "Showed properties on Google Maps"}
            )
        except Exception:
            st.error("Failed to display properties on Google Maps.")
            st.session_state.messages.append(
                {"role": "assistant", "content": "Failed to display properties on Google Maps"}
            )

    else:
        st.warning("Unexpected result type received.")
        st.session_state.messages.append(
            {"role": "assistant", "content": "Unexpected result type received."}
        )
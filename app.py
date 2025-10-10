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

st.markdown("<h1 style='font-size: 40px;'>🏠 London Real Estate Chat Assistant</h1>", unsafe_allow_html=True)

# -------------------
# Session State Setup
# -------------------
if "messages" not in st.session_state:
    st.session_state.messages = deque(maxlen=12)

# -------------------
# Show Conversation History
# -------------------

def render_thumbs(i):
    # Center thumbs and keep them out of chat history
    col1, col2, col3 = st.columns([1, 0.2, 1])
    with col1:
        pass  # left spacer
    with col2:
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("👍", key=f"up_{i}", use_container_width=True):
                st.toast("Thanks for your feedback 👍")
        with c2:
            if st.button("👎", key=f"down_{i}", use_container_width=True):
                st.toast("Got it — we’ll improve 👎")
    with col3:
        pass  # right spacer

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        # If the message includes a saved dataframe, render it directly
        if msg.get("type") == "data" and "data" in msg:
            st.dataframe(pd.DataFrame(msg["data"]), use_container_width=True)
        else:
            st.markdown(msg["content"])

        # Only add thumbs to assistant messages
        if msg["role"] == "assistant":
            render_thumbs(i)

if len(st.session_state.messages) == 0:

    st.markdown(
        """
        <div style='text-align: center; padding: 8px 0;'>
            <h3>💬 What this chatbot can do</h3>
            <p style='font-size:20px; color:grey;'>
                Explore real-time insights from London’s property market:
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- Top Large Image ---
    st.markdown("<br>", unsafe_allow_html=True)  # spacing between title and top image
    col_center = st.columns([0.5, 2, 0.5])[1]  # center the top image

    with col_center:
        st.markdown(
            "<p style='text-align:center; font-size:26px; font-weight:600;'>🏘️ Estimate property prices by prompting their URL</p>",
            unsafe_allow_html=True,
        )
        st.image("assets/ai_price.png", use_container_width=True, output_format="PNG", caption=None)

    # Add spacing before next row
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

    # --- Three Smaller Images Below ---
    cols = st.columns(3)
    img_style = {"use_container_width": True}

    for i, (caption, img) in enumerate([
        ("📊 View property/data tables", "assets/pic3.png"),
        ("🗺️ Show properties on maps", "assets/pic1.png"),
        ("📈 Generate rent analytics plots", "assets/pic2.png"),
    ]):
        with cols[i]:
            st.markdown(
                f"<p style='text-align:center; font-size:22px; font-weight:600;'>{caption}</p>",
                unsafe_allow_html=True,
            )
            st.image(img, width=500)  # smaller than full container width for subtle shrink

    st.markdown("<hr style='margin: 5px 0;'>", unsafe_allow_html=True)


# -------------------
# User Input
# -------------------
query = st.chat_input("Ask about London properties...")

# -------------------
# Query Handling
# -------------------
if query:
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append({"role": "user", "content": query})

    final_query = contextualize_query(query, history=st.session_state.messages)
    # For debugging only
    # st.caption(f"Contextualized query → {final_query}")

    with st.spinner("Processing your query..."):
        result = main_agent(final_query)

    result_type = result.get("type")

    # -------------
    # Error message
    # -------------
    if result_type == "error":
        st.error(result["error"])
        st.session_state.messages.append(
            {"role": "assistant", "content": result["error"]}
        )

    # -------------
    # Text message
    # -------------
    elif result_type == "message":
        st.info(result["message"])
        st.session_state.messages.append(
            {"role": "assistant", "content": result["message"]}
        )

    # -------------
    # Dataframe result ✅ (logic-based)
    # -------------
    elif result_type == "data":
        st.success("Here is the data related to your query:")
        df = pd.DataFrame(result["data"])
        st.dataframe(df, use_container_width=True)

        # Truncate a preview for chat history
        df_sample = df.head(3).copy()
        for col in df_sample.columns:
            df_sample[col] = df_sample[col].astype(str).str.slice(0, 40) + "…"

        # Store full data for rerendering + markdown for reference
        st.session_state.messages.append(
            {
                "role": "assistant",
                "type": "data",
                "data": result["data"],   # store original data
                "content": f"Returned data sample:\n\n{df_sample.to_markdown(index=False)}",
            }
        )

    # -------------
    # Plot result (unchanged)
    # -------------
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
    # -------------
    # HTML result (e.g., map)
    # -------------
    elif result_type == "html":
        try:
            html_code = result.get("content")
            components.html(html_code, height=600)
            st.session_state.messages.append(
                {"role": "assistant", "content": "🗺️ Displayed properties on Google Maps."}
            )
        except Exception:
            st.error("Failed to display properties on Google Maps.")
            st.session_state.messages.append(
                {"role": "assistant", "content": "❌ Failed to display properties on Google Maps."}
            )
    # -------------
    # Properties valuation results,
    # These are not added to the chat history
    # -------------
    elif result_type == "pricing_data":
        st.success("Here are your properties valuations:")
        df = pd.DataFrame(result["data"])
        st.dataframe(df, use_container_width=True)

    # -------------
    # Unexpected result type
    # -------------
    else:
        st.warning("Unexpected result type received.")
        st.session_state.messages.append(
            {"role": "assistant", "content": "⚠️ Unexpected result type received."}
        )
    # Rerender the last assistant message with thumbs
    render_thumbs(len(st.session_state.messages) - 1)

# reset button
if st.button("🔄 Restart Conversation"):
    st.session_state.messages.clear()
    st.rerun()  # refresh the app
---
title: Chatbot
emoji: 🤖
colorFrom: blue
colorTo: pink
sdk: streamlit
sdk_version: "1.38.0"
app_file: app.py
pinned: false
---



# 🧠 AI_DUBAI_CRYPTO_CLOUD

A Streamlit-based GenAI/AGI and AI project integrating London real estate real estate data with advanced AI tools for data analysis, visualization, and geospatial mapping.

---

## Chatbot logic 

```md
User Query
   ↓
[1] Relevance Check (is_uae_real_estate_query)
   → If irrelevant → "This is an irrelevant question to UAE property."
   ↓
[2] Data Intent Extraction (extract_data_intent)
   → e.g., "monthly count of properties added in Dubai"
   ↓
[3] Data Processing (safe_dataframe_tool using PandasAI)
   → Uses the data intent string to build a pandas-safe query
   ↓
[4] User Goal Classification (llm_classifier)
   → e.g., "output", "plot_stats", or "geospatial_plot"
   ↓
[5] Execute Action
   - if "output" → return raw data
   - if "plot_stats" → call visualize_tool
   - if "geospatial_plot" → generate Google Maps HTML 

```
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

A Streamlit-based AI project integrating UAE real estate

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




## 📁 Project Structure
```md
├── app.py # Main Streamlit app
├── data # Local data
│ ├── dubai.geojson
│ └── uae_real_estate_2024.csv
├── exports # Plot files
│ └── charts
│ └── temp_chart.png
├── notebooks # Jupyter notebooks for prototyping
│ ├── agent_with_tools.ipynb
│ └── EDA.ipynb
├── requirements.txt # Python dependencies
├── README.md # Project description
└── src # Source code
├── classifiers.py # Classification routing models
├── process_data.py # Data processing utilities
└── tools.py # LangChain tools
```
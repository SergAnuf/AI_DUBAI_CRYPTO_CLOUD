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

A Streamlit-based AI project integrating London real estate data with advanced AI tools for data analysis, visualization, and geospatial mapping.

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
### Project Structure

- `app.py` – Main Streamlit app, run by Dockerfile
- `datasets/new-bot/rental-data-london2/`
  - `data.parquet` – Primary scrapped properties dataset
  - `schema.yaml` – Schema for PandasAI, helps with LLM data understanding 
- `src/`
  - `agent.py` – Core ChatBot logic
  - `classifiers.py` – Includes functions for relevance checking and goal classification
  - `tools.py` – LLM tools include: 
  -      data extraction, plotly code generation, contextualize_query function(query, history) -> new_query
  - `geo_tools.py` – Utilities to map properties on Google Maps, works as long as properties have ids 
- `prompts/`
   - 'c'
- pandasai.log – Log file for PandasAI operations
- `tests/` - tests folder, in progress


- Dockerfile – Containerization for HuggingSpace deployment
- clear_streamlit_cache.sh – Script to clear Streamlit cache
- run_tests.sh - Script to run unit tests (pytest), in progress.

### Requirements
- Python 3.10  
- `requirements.txt`


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


### Project Structure:

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
   - `classifiers.py` - Prompts for relevance and goal classification
   - `tool_prompts.py` - Prompts for data extraction and visualization tools. 
   Includes "format_query_with_table_output(query) -> query" function that augments pandas ai query with table output request
   - `tool_description.py`- Descriptions for each tool used by the agent (not used now)
- `notebooks/`
  - `upload_london_data.ipynb` - Notebook used to upload London properties data to PandasAI
- pandasai.log – Log file for PandasAI operations, can be cleared by bash command " > pandasai.log "  
- `tests/` - tests folder, in progress

### Scripts:
- clear_streamlit_cache.sh – Script to clear Streamlit cache (rarely needed)
- run_tests.sh - Script to run unit tests (pytest), in progress.

### Requirements:
- Python 3.10  
- `requirements.txt`  – Python dependencies
- Dockerfile – Containerization for HuggingSpace deployment


## ChatBot logic 

```md
User Query
   ↓
[1] Relevance Check (is_uae_real_estate_query)
   → If irrelevant → "This is an irrelevant question to London property."
   ↓ pass User Query
[2] Data Processing (safe_dataframe_tool using PandasAI)
   → If error → "Returns error message"
   ↓ Uses the User Query and returns a DataFrame or relevant data
[3] User Goal Classification (llm_classifier)
   → e.g., "output", "plot_stats", or "geospatial_plot"
   ↓
[4] Execute Action
   - if "output" → return raw data
   - if "plot_stats" → call visualize_tool 
   - if "geospatial_plot" → generate Google Maps HTML 


Conversation is maintained by:

a. Logs history at step [4] as list of (User Query, step 4 output, errors) -> history
b. Creates new query with context: contextualize_query(query, history) -> new_query
c. Passes new_query to step [1]. 
d. Loop continues until user stops.
```


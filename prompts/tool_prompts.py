import pandas as pd
from src.utils.env_tools import cache_resource
import yaml

with open("datasets/new-bot/rental-data-london3/schema.yaml", "r") as f:
    SCHEMA_YAML_CONTENT = yaml.safe_load(f)


def format_query_with_table_output(original_query: str, action: str) -> str:
    """
    Formats the user query with strict table output instructions.
    Adds extra guidance for geospatial queries so PandasAI can handle distance-based
    questions correctly without causing SQL execution errors in DuckDB.
    """

    # --- Shared instruction ---
    base_instruction = """
      Output format requirement:
      - Present all results strictly as a table (rows and columns).
      - Do not return pictures, charts, or maps.
      - If there is only one value, still return it as a one-row, one-column table.
      - Use clear column headers.
      - Price sort always comes latest
    """

    # --- Geospatial extension ---
    geo_extension = """
      Geospatial rule:
      - If the user query mentions proximity (e.g. “closest to”, “near”, or “distance from” a place or station):
          * Identify the place or station name from the query (e.g. “Camden Town Station”).
          * Retrieve its geographic coordinates (latitude, longitude) if available.
          * Fetch relevant data using a standard SQL query — do NOT compute distances directly in SQL.
          * Do not add arbitrary SQL LIMITs
          * After fetching the data, compute the geographic distance in Python using latitude and longitude columns
            (for example, with the Haversine formula).
          * Sort the results by this computed distance in ascending order.
          * Never call or define a Haversine or trigonometric function inside SQL.
      - Always include the 'id' column if properties are returned.
    """
    # --- Combine instructions based on action type ---
    if action == "geospatial_plot":
        return original_query.strip() + "\n\n" + base_instruction + geo_extension
    else:
        return original_query.strip() + "\n\n" + base_instruction



def get_user_data_intent(user_query: str) -> str:
    schema_data = yaml.safe_load(SCHEMA_YAML_CONTENT)
    columns_info = schema_data['columns']

    schema_representation = ", ".join([col['name'] for col in columns_info])

    prompt = f"""
You are an assistant that reformulates user queries into schema-aware queries 
that PandasAI can execute, while keeping natural language flexibility.

Dataset columns: {schema_representation}

User query: "{user_query}"

Rewrite the query so that it:
- Uses the column names when possible  
- Still keeps flexible natural phrasing (don’t force SQL logic)  
- Ensures references like 'furnished', 'single room', 'Westminster' 
  can map to any relevant text column (title, description, property_type, borough, furnish_type)
-  For spatial queries (e.g., maps) include required fields like latitude and longitude.

Return just the rewritten query (natural language, schema-aware).
"""
    return prompt



def get_plotly_code_prompt(user_input: str, data: pd.DataFrame) -> str:
    schema = ", ".join(data.columns)
    sample = data.head(5).to_dict(orient="records")

    return f"""
You are an assistant that generates **only Python code** using Plotly (not matplotlib).

The dataset is already available in memory as a variable named `df`.

Dataset columns: {schema}
Sample rows (first 5, for reference only — do NOT hardcode them): {sample}

User request: "{user_input}"

Instructions:
- Always use the full dataset `df` (not just the sample).
- Do not recreate or hardcode the dataset.
- If there is only one row, still plot it (e.g., single bar or single point).
- Choose the most appropriate plot type (bar, line, scatter, histogram, etc.).
- Return only valid Python code, wrapped like this:

```python
# code here
"""

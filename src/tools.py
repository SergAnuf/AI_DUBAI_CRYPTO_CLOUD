# Standard libraries
import os
import io
from typing import Dict, Any

# Third-party libraries
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dotenv import load_dotenv

# LangChain and OpenAI
from langchain.agents import tool
from langchain.tools import tool  # If both needed, clarify usage to avoid conflict

# pandasai
from pandasai import SmartDataframe

# Local modules
from src.process_data import change_data_type
import pandasai.llm
import openai

# Usage in 25 defined model used for pandas ai:
pandas_ai = pandasai.llm.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  
official_ai = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


load_dotenv()


DESCRIPTION_SELECT_CALCULATE = """
Safely query a real estate dataset of Dubai properties. Returns DataFrames only, never visualizations.

Good for:
- Finding cheapest or most expensive listings
- Filtering by bedrooms, price, location, etc.
- Tabular queries

Examples:
- "Find 10 cheapest properties in Dubai"
- "Show all villas with 3+ bedrooms and sea view"
"""

DESCRIPTION_PLOT = """
Generate visualizations for the Dubai property dataset using Plotly Express.

Good for:
- Plotting price distributions
- Comparing average prices by location or property type
- Time trends

Examples:
- "Plot price histogram for apartments in Marina"
- "Show average price by property type"

Returns tuple:

- plotly figure
- figure type
- code to generate the figure 

"""

# PATH_DATA = "../data/uae_real_estate_2024.csv"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# PATH_DATA = os.path.join(BASE_DIR, "..", "data", "uae_real_estate_2024.csv")
PATH_DATA = os.path.join(BASE_DIR,"..", "data", "uae_real_estate_2024_geo_ready2.parquet")


@tool(description=DESCRIPTION_SELECT_CALCULATE)
def safe_dataframe_tool(
    query: str,
) -> Dict[str, Any]:
    """
    Performs calculations on tabular data from CSV.
    Returns results in a JSON-serializable format.
    """
    try:
        # Configure with error correction
        llm = pandas_ai
        # data = change_data_type(pd.read_csv(PATH_DATA))
        data = pd.read_parquet(PATH_DATA)
        smart_df = SmartDataframe(data, config={
            "llm": llm,
            "open_charts": False,
            "enable_cache": True,
            "verbose": False,
            "use_error_correction_framework": True,
            "max_retries": 3
        })

        # Execute query -> Force table only
        result = smart_df.chat(
            f"Return as table: {query}",
            output_type="dataframe"
        )
        
        # Convert to JSON-serializable format
        if isinstance(result, pd.DataFrame):
            return result.to_dict(orient="records")
              
    except Exception as e:
        return {
            "error": str(e),
            "success": False,
            "solution": "Try simplifying your query or check data columns"
        }



def generate_plot_prompt(data: list[dict], query: str) -> str:
    """Generates clean plotting code from data (list of dicts) and a query"""
    columns = ", ".join(data[0].keys())
    sample = data[:2]  # Show first 2 rows as example
    
    return f"""
Create Plotly Express code to visualize this data:
Columns: {columns}
Sample rows: {sample}

Query: "{query}"

Requirements:
1. First create DataFrame: df = pd.DataFrame(data)
2. Use px (Plotly Express) which is already imported
3. Don't modify or filter the data
4. Save plot to variable 'fig'
5. Only return the Python code (no text or markdown)
6. Query can include plotting settings 

Example:
```python
df = pd.DataFrame(data)
fig = px.bar(df, x='country', y='sales', title='Sales by Country')
fig.update_layout(xaxis_title='Country', yaxis_title='Sales')"""


def create_plot_code(data: list[dict], query: str) -> str:
    """Generates plotting code using OpenAI"""
    prompt = generate_plot_prompt(data, query)
    
    response = official_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    
    code = response.choices[0].message.content
    code = code.replace("```python", "").replace("```", "")
    code = code.strip()
    
    return code
    
    
        
        
@tool(description=DESCRIPTION_PLOT)
def visualize_tool(data: list[dict], query: str) -> dict:
    """Executes plotting code and returns results"""
    try:
        code = create_plot_code(data, query)
        df = pd.DataFrame(data)
        
        exec_globals = {
            "pd": pd,
            "px": px,
            "go": go,
            "data": data,
            "df": df
        }
        exec(code, exec_globals)
        
        fig = exec_globals.get("fig")
        if fig is None:
            raise ValueError("No figure was created - missing 'fig' variable")
        
        buf = io.BytesIO()
        if hasattr(fig, "write_image"):  # Plotly
            fig.write_image(buf, format="png")
        else:
            raise ValueError(f"Unsupported figure type: {type(fig)}")
        
        buf.seek(0)  # Reset buffer position for reading in Streamlit

        return {
            "image_bytes": buf,  # Return BytesIO object instead of base64 string
            "code": code,
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "code": code if 'code' in locals() else "",
            "success": False
        }

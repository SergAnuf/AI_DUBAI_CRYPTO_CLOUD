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
# from langchain.agents import tool
from langchain.tools import tool  # If both needed, clarify usage to avoid conflict

# pandasai
import pandasai as pai

# Local modules
import openai
from src.utils.env_tools import cache_resource

from prompts.tool_description import DESCRIPTION_SELECT_CALCULATE, DESCRIPTION_PLOT
from prompts.plot_prompt import generate_plot_prompt


# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_DATA = os.path.join(BASE_DIR,"..", "data", "uae_real_estate_2024_geo_ready2.parquet")


load_dotenv()


@cache_resource
def get_openai_llm():
    return openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@cache_resource
def load_pandas_ai_dataframe():
    """Load the real estate dataset from Parquet file."""
    return pai.load("my-org/properties2")



def extract_data_intent(user_query: str) -> str:
    prompt = f"""
You are a helpful assistant that extracts the data requirements from a user's question.

Only extract and return what data is needed — specifically filtering, aggregation, or selection criteria — without mentioning how the data will be used or visualized.

Return a concise description of the data subset or aggregation to be retrieved.

User query:
\"\"\"{user_query}\"\"\"

Data intent:
"""

    official_ai = get_openai_llm()
    response = official_ai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You extract data intent only. Do not mention visualization or usage."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=100,
    )
    
    return response.choices[0].message.content.strip()


@tool(description=DESCRIPTION_SELECT_CALCULATE)
def safe_dataframe_tool(query: str) -> Dict[str, Any]:
    """
    Executes a natural language query on the UAE real estate dataset.
    """
    try:
        data = load_pandas_ai_dataframe()  
        result = data.chat(query).to_dict()
        
        if result["error"] is None:
            return result["value"].to_dict(orient="records")
        
        else:
            return {
                "error": result["error"],
                "success": False,
                "solution": "Check your query syntax or the dataset structure."
            }
    
    except Exception as e:
        return {
            "error": str(e),
            "success": False,
            "solution": "Check your query syntax or the dataset structure."
        }



def create_plot_code(data: list[dict], query: str) -> str:
    """Generates plotting code using OpenAI"""
    prompt = generate_plot_prompt(data, query)
    
    official_ai = get_openai_llm()
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
    """Executes plotting code and returns picture bytes and code"""
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

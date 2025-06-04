# Standard libraries
import os
import json
from typing import Optional
from dotenv import load_dotenv 

# Third-party libraries
import openai
import pandasai as pai
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from langchain.tools import tool 
import matplotlib.pyplot as plt
from pandasai_openai import OpenAI


# Local modules
from src.utils.env_tools import cache_resource
from prompts.tool_description import DESCRIPTION_GET_USER_DATA_REQUIREMENTS, \
                                     DESCRIPTION_GET_DATA,\
                                     DESCRIPTON_GENERATE_PLOT_CODE
                                     
load_dotenv()   

                             
# Global Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@cache_resource
def get_openai_llm():
    return openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@cache_resource
def load_pandas_ai_dataframe():
    """Load the real estate dataset from created Pandas AI directory."""
    return pai.load("my-org/clean2")

def set_pandas_llm():
    llm = OpenAI(api_token=os.getenv("OPENAI_API_KEY"),model="gpt-4")
    pai.config.set({"llm": llm})


set_pandas_llm()


def standard_response(success: bool, result=None, error=None, solution=None) -> str:
    if isinstance(result, pd.DataFrame):
        result = json.loads(result.to_json(date_format='iso', orient='records'))  # Parse into list of dicts
    return json.dumps({
        "success": success,
        "result": result if success else None,
        "error": None if success else error,
        "solution": None if success else solution
    })
    
    
@tool(description=DESCRIPTION_GET_USER_DATA_REQUIREMENTS)
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

@tool(description=DESCRIPTION_GET_DATA)
def safe_dataframe_tool(query: str) -> str:
    """
    Executes a natural language query on the UAE real estate dataset.
    Returns a standardized JSON-formatted string.
    """
    try: 
        data = load_pandas_ai_dataframe()
        result = data.chat(query).to_dict()

        if result["error"] is None and "value" in result:
            return standard_response(
                success=True,
                result=result["value"]
            )
        else:
            return standard_response(
                success=False,
                error=result["error"],
                solution="Check your query syntax or the dataset structure."
            )

    except Exception as e:
        return standard_response(
            success=False,
            error=str(e),
            solution="Check your query syntax or the dataset structure."
        )



def extract_python_code(text: str) -> Optional[str]:
    """
    Extract Python code from markdown code blocks.
    Returns None if no code found.
    """
    if '```python' in text:
        return text.split('```python')[1].split('```')[0].strip()
    elif '```' in text:
        return text.split('```')[1].split('```')[0].strip()
    return None


@tool(description=DESCRIPTON_GENERATE_PLOT_CODE)
def create_plotly_code(input_json: str):
    """Generate and execute Plotly code using your exact prompt format"""
    
    parsed = json.loads(input_json)
    result = parsed["data"]
    user_input = parsed["query"]
    # Prepare data
    data = pd.DataFrame(result)
    
    # Create prompt (using your exact format)
    code_prompt = f"""
        Generate the code <code> for plotting the data, {data}, in plotly,
        in the format requested by: {user_input}.
        The solution should be given using plotly and only plotly.
        Do not use matplotlib. Return the code <code> in the following
        format python <code>
    """
    # Get AI response
    official_ai = get_openai_llm()
    response = official_ai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": code_prompt}],
        max_tokens=1000
    )
    
    # Extract code
    raw_response = response.choices[0].message.content
    code = extract_python_code(raw_response)

    # Modify code for Streamlit
    code = code.replace("fig.show()", "")
    code += "\nst.plotly_chart(fig, use_container_width=True)"
    
    return standard_response(
                success=True,
                result=code
            )
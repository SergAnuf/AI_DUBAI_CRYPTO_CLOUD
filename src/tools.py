# Standard libraries
import os
import json
from typing import Optional
from dotenv import load_dotenv

# Third-party libraries
import openai
import pandasai as pai
import pandas as pd
from langchain.tools import tool
from pandasai_openai import OpenAI
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

# Local modules
from src.utils.env_tools import cache_resource
from prompts.tool_prompts import get_user_data_intent, format_query_with_table_output, get_plotly_code_prompt
from prompts.tool_description import DESCRIPTION_GET_USER_DATA_REQUIREMENTS, \
    DESCRIPTION_GET_DATA, \
    DESCRIPTON_GENERATE_PLOT_CODE

load_dotenv()


@cache_resource
def get_openai_llm():
    return openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@cache_resource
def load_pandas_ai_dataframe():
    """Load the real estate dataset from created Pandas AI directory."""
    return pai.load("new-bot/london-rental-data")


def set_pandas_llm():
    llm = OpenAI(api_token=os.getenv("OPENAI_API_KEY"), model="gpt-4")
    pai.config.set({"llm": llm})


set_pandas_llm()


def standard_response(success: bool, result=None, error=None, solution=None) -> str:
    if isinstance(result, pd.DataFrame):
        result = json.loads(result.to_json(date_format='iso', orient='records'))  # Parse into the list of dicts
    elif isinstance(result, pd.Series):
        result = result.to_dict()  # convert Series to dict
    return json.dumps({
        "success": success,
        "result": result if success else None,
        "error": None if success else error,
        "solution": None if success else solution
    })


@tool(description=DESCRIPTION_GET_USER_DATA_REQUIREMENTS)
def extract_data_intent(user_query: str) -> str:
    prompt = get_user_data_intent(user_query)
    official_ai = get_openai_llm()
    response = official_ai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            ChatCompletionSystemMessageParam(role="system", content="You extract data intent only. Do not mention "
                                                                    "visualization or usage."),
            ChatCompletionUserMessageParam(role="user", content=prompt)
        ],
        temperature=0,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()


@tool(description=DESCRIPTION_GET_DATA)
def safe_dataframe_tool(query: str) -> str:
    """
    Executes a natural language query on the London real estate dataset.
    Returns a standardized JSON-formatted string.
    """
    try:
        data = load_pandas_ai_dataframe()
        result = data.chat(format_query_with_table_output(query)).to_dict()

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
    Extract Python code from Markdown code blocks or HTML code tags.
    Returns None if no code found.

    Handles these cases:
    1. ```python\ncode\n```
    2. ```\ncode\n```
    3. <code>\ncode\n</code>
    """
    # Case 1: Python markdown
    if '```python' in text:
        return text.split('```python')[1].split('```')[0].strip()
    # Case 2: Regular markdown
    elif '```' in text:
        return text.split('```')[1].split('```')[0].strip()
    # Case 3: HTML code tags
    elif '<code>' in text.lower():
        return text.split('<code>')[1].split('</code>')[0].strip()
    return None


@tool(description=DESCRIPTON_GENERATE_PLOT_CODE)
def create_plotly_code(input_json: str):
    """Generate and execute Plotly code using your exact prompt format"""

    parsed = json.loads(input_json)
    result = parsed["data"]
    user_input = parsed["query"]
    # Prepare data
    if isinstance(result, dict):
        # Wrap in list to make it a single-row DataFrame
        result = [result]

    data = pd.DataFrame(result)
    # Create prompt (using your exact format)
    code_prompt = get_plotly_code_prompt(user_input, data)
    # Get AI response
    official_ai = get_openai_llm()
    response = official_ai.chat.completions.create(
        model="gpt-4.1-mini",
        messages=
        [
            ChatCompletionSystemMessageParam(role="system",
                                             content="You create Plotly code based on user_input and data"),
            ChatCompletionUserMessageParam(role="user", content=code_prompt)
        ],
        max_tokens=400
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

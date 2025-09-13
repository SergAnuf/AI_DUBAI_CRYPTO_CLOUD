import pandas as pd
from src.utils.env_tools import cache_resource
import yaml


@cache_resource
def load_data():
    return pd.read_parquet('s3://anufriev/sample_data.parquet', engine='pyarrow')


def format_query_with_table_output(original_query):
    table_format_instruction = """
Output format:  
Present the results in a structured **table format**   
"""
    return original_query + table_format_instruction


SCHEMA_YAML_CONTENT = """
name: clean2
source:
  type: parquet
  path: data.parquet
columns:
- name: title
  type: string
  description: Title of the listing
- name: bathrooms
  type: integer
  description: Number of bathrooms
- name: bedrooms
  type: integer
  description: Number of bedrooms
- name: type
  type: string
  description: Type of the property
- name: price
  type: integer
  description: Price of the property
- name: verified
  type: boolean
  description: Whether listing is verified
- name: priceDuration
  type: string
  description: Price duration type (e.g., per month)
- name: sizeMin
  type: integer
  description: Minimum size of the property
- name: furnishing
  type: string
  description: Furnishing status of the property
- name: description
  type: string
  description: Text description of the listing
- name: latitude
  type: float
  description: Latitude coordinate
- name: longitude
  type: float
  description: Longitude coordinate
- name: City
  type: string
  description: City where the property is located
- name: addedOn_year_month
  type: datetime
  description: Year and month of added date (YYYY-MM)
- name: addedOn_month_name
  type: string
  description: Month name of the added date
- name: addedOn_month_num
  type: integer
  description: Month number of the added date
- name: addedOn_day_num
  type: integer
  description: Day number of the added date
- name: Area
  type: string
  description: Area or neighborhood of the property
"""


def get_user_data_intent(user_query: str) -> str:
    # Load the schema from the YAML content
    schema_data = yaml.safe_load(SCHEMA_YAML_CONTENT)
    columns_info = schema_data['columns']

    # Format column details for the prompt.
    # This provides name, type, and description for each column clearly.
    schema_representation = "Column Name (Type): Description\n"
    schema_representation += "---------------------------------\n"
    for col in columns_info:
        schema_representation += f"{col['name']} ({col['type']}): {col['description']}\n"

    prompt = f"""
    Here is the schema of the dataset you are working with:
    {schema_representation}

    Based on the user query: "{user_query}", extract the following information:

    1. **Data intent**: Describe the final table to be produced — including what columns it should have, how rows are
    grouped or labeled, and what comparisons or computations are required. For spatial queries (e.g., maps),
    include required fields like latitude and longitude.

    2. **Data logic**: List the exact step-by-step operations needed to create this table from the dataset —
    including filtering conditions, groupings, joins, aggregations, computations, and any spatial or temporal logic.

    Provide your answer in two clearly labeled sections:

    Data intent:
    <your description here>

    Data logic:
    <your description here>
    """
    return prompt


def get_plotly_code_prompt(user_input: str, data: pd.DataFrame) -> str:
    return f"""
        Generate the code <code> for plotting the data, {data}, in plotly,
        in the format requested by: {user_input}.
        The solution should be given using plotly and only plotly.
        Do not use matplotlib. Return the code <code> in the following
        format python <code>
    """

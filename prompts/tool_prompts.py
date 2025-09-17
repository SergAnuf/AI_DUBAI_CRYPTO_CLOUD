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
name: london_rental_data
source:
  type: parquet
  path: data.parquet
description: London real estate property listings with pricing, size, location, station
  proximity, and noise levels
columns:
- name: id
  type: string
  description: Unique identifier for each property listing
- name: title
  type: string
  description: Listing title
- name: display_address
  type: string
  description: Readable address of the property
- name: postcode_outcode
  type: string
  description: Outcode part of the UK postcode
- name: postcode_incode
  type: string
  description: Incode part of the UK postcode
- name: bathrooms
  type: integer
  description: Number of bathrooms
- name: bedrooms
  type: integer
  description: Number of bedrooms
- name: property_type
  type: string
  description: Type of property (flat, apartment, house, etc.)
- name: price_gbp
  type: float
  description: Listed price in GBP
- name: secondary_price_gbp
  type: float
  description: Secondary listing price (e.g. weekly rent) in GBP
- name: let_available_date
  type: datetime
  description: Date property is available to let, if known
- name: deposit_included_or_not
  type: string
  description: 'Deposit included or (e.g '
- name: let_type
  type: string
  description: Letting type (short term, long term)
- name: furnish_type
  type: string
  description: Furnishing type (furnished, unfurnished, part furnished)
- name: council_tax_exempt
  type: boolean
  description: Whether council tax is exempt
- name: council_tax_included
  type: boolean
  description: Whether council tax is included in rent
- name: council_tax_band
  type: string
  description: Council tax band classification
- name: property_features
  type: string
  description: Key features of the property, e.g. garden, parking
- name: listing_update_reason
  type: string
  description: Reason for most recent listing update
- name: listing_update_date
  type: datetime
  description: Date of last listing update
- name: first_visible_date
  type: datetime
  description: Date listing first became visible
- name: added_on
  type: datetime
  description: Date property was added to the platform
- name: size_sqft_min
  type: float
  description: Minimum property size in square feet
- name: size_sqft_max
  type: float
  description: Maximum property size in square feet
- name: latitude
  type: float
  description: Latitude of the property
- name: longitude
  type: float
  description: Longitude of the property
- name: nearest_station1_name
  type: string
  description: Name of the nearest station
- name: nearest_station2_name
  type: string
  description: Name of the second nearest station
- name: nearest_station3_name
  type: string
  description: Name of the third nearest station
- name: nearest_station1_distance_km
  type: float
  description: Distance to nearest station in km
- name: nearest_station2_distance_km
  type: float
  description: Distance to second nearest station in km
- name: nearest_station3_distance_km
  type: float
  description: Distance to third nearest station in km
- name: nearest_station1_type
  type: string
  description: Type of nearest station (tube, national train, DLR, etc.)
- name: nearest_station2_type
  type: string
  description: Type of second nearest station
- name: nearest_station3_type
  type: string
  description: Type of third nearest station
- name: borough
  type: string
  description: London borough of the property
- name: travel_zone
  type: string
  description: London Travelcard zone
- name: distance_to_center_km
  type: float
  description: Distance from property to central London (Charing Cross)
- name: noise_level_class
  type: string
  description: Noise classification (low, medium, high, no_data)
- name: description
  type: string
  description: Cleaned free-text property description
"""


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


# def get_user_data_intent(user_query: str) -> str:
#     # Load the schema from the YAML content
#     schema_data = yaml.safe_load(SCHEMA_YAML_CONTENT)
#     columns_info = schema_data['columns']
#
#     # Format column details for the prompt.
#     # This provides name, type, and description for each column clearly.
#     schema_representation = "Column Name (Type): Description\n"
#     schema_representation += "---------------------------------\n"
#     for col in columns_info:
#         schema_representation += f"{col['name']} ({col['type']}): {col['description']}\n"
#
#     prompt = f"""
#     Here is the schema of the dataset you are working with:
#     {schema_representation}
#
#     Based on the user query: "{user_query}", extract the following information:
#
#     1. **Data intent**: Describe the final table to be produced — including what columns it should have, how rows are
#     grouped or labeled, and what comparisons or computations are required. For spatial queries (e.g., maps),
#     include required fields like latitude and longitude.
#
#     2. **Data logic**: List the exact step-by-step operations needed to create this table from the dataset —
#     including filtering conditions, groupings, joins, aggregations, computations, and any spatial or temporal logic.
#
#     Provide your answer in two clearly labeled sections:
#
#     Data intent:
#     <your description here>
#
#     Data logic:
#     <your description here>
#     """
#     return prompt


# def get_plotly_code_prompt(user_input: str, data: pd.DataFrame) -> str:
#     return f"""
#         Generate the code <code> for plotting the data, {data}, in plotly,
#         in the format requested by: {user_input}.
#         The solution should be given using plotly and only plotly.
#         Do not use matplotlib. Return the code <code> in the following
#         format python <code>
#     """


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

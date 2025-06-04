# This file contains descriptions for various tools used in the application.

DESCRIPTION_GET_DATA = """
Safely query a real estate dataset of Dubai properties. Returns DataFrames only, never visualizations.

Good for:
- Finding cheapest or most expensive listings
- Filtering by bedrooms, price, location, etc.
- Tabular queries

Examples:
- "Find 10 cheapest properties in Dubai"
- "Show all villas with 3+ bedrooms and sea view"
"""


DESCRIPTON_GENERATE_PLOT_CODE = """
Create Python code to generate a Matplolib figure based on a query and dataset.
"""


DESCRIPTION_CREATE_PLOT = """
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

DESCRIPTION_GET_USER_DATA_REQUIREMENTS = """
Given a user query, extract the data requirements without mentioning how the data will be used or visualized.
Return a concise description of the data subset or aggregation to be retrieved.
"""
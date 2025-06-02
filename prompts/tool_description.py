""" Tool descriptions for the Dubai real estate dataset queries. """



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
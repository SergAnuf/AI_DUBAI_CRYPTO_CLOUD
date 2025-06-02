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
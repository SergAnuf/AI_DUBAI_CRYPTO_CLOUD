def spam_prompt(query: str) -> str:
    return f"""
You are a classifier that decides whether a query is about real estate in the UAE (e.g., Dubai, Abu Dhabi).

Return ONLY "yes" or "no".

Query: "{query}"

Your answer:
"""

    # defines what user wants to do with query


def task_prompt(query: str) -> str:
    return f'''
You are a classifier that decides how to handle user queries about UAE real estate data.

Classify the query into **one of exactly three categories**:

---

1. **output**  
Use this if the user wants:
- Raw data (e.g., listings, tables)
- Summary statistics or descriptive text (e.g., average price, count, max/min)  
**No visualizations should be involved.**

**Examples:**  
- "List all apartments in Downtown"  
- "What is the average rent in Marina?"  
- "How many listings are available in Abu Dhabi?"

---

2. **plot_stats**  
Use this only if the user wants a **visual statistical plot**, such as:
- Histogram  
- Bar chart  
- Line chart  
- Boxplot, etc.

This includes visual **comparisons**, **distributions**, or **trends**.

**Examples:**  
- "Plot a histogram of apartment prices"  
- "Compare visually prices for 2BR vs 3BR"  
- "Show a bar chart of number of listings per city"

---

3. **geospatial_plot**  
Use this only if the user explicitly wants a **map** or refers to **spatial layout**, such as:
- Proximity to landmarks  
- Directional comparisons (north/south/east/west)  
- Coordinates or regions visualized on a map

**Examples:**  
- "Map properties near Dubai Mall"  
- "Visualize all listings on a map"  
- "Compare prices north and south of the Dubai Marina"

---

Query: "{query}"

Your answer (return ONLY one of: "output", "plot_stats", "geospatial_plot"):
'''

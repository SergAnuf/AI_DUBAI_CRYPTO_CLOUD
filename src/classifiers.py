import openai
import os



official_ai = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def is_uae_real_estate_query(query: str) -> bool:
    prompt = f"""
You are a classifier that decides whether a query is about real estate in the UAE (e.g., Dubai, Abu Dhabi).

Return ONLY "yes" or "no".

Query: "{query}"

Your answer:
"""
    response = official_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=3,
    )
    decision = response.choices[0].message.content.strip().lower()
    return decision == "yes"



def llm_classifier(query: str) -> str:
    # LLM classification
    prompt = f"""
You are a classifier that decides how to handle the query about UAE properties.

Return one of three strings ONLY:
- "output" (just output data),
- "plot_stats" (plot statistics like histograms, bar charts),
- "geospatial_plot" (plot maps/geospatial charts).

Query: "{query}"

Your answer:
"""
    response = official_ai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=10,
    )
    decision = response.choices[0].message.content.strip().strip('"').lower()
    print(decision)
    return decision
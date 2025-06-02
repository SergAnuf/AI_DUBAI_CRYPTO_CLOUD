def spam_prompt(query: str) -> str:
    return f"""
You are a classifier that decides whether a query is about real estate in the UAE (e.g., Dubai, Abu Dhabi).

Return ONLY "yes" or "no".

Query: "{query}"

Your answer:
""" 


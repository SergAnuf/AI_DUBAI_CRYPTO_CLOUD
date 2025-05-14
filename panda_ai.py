from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API key not found. Check your .env file and variable name.")

from pandasai.llm import OpenAI
from pandasai import SmartDataframe
import pandas as pd

llm = OpenAI(api_key=api_key)


data = pd.read_csv("data/uae_real_estate_2024.csv")

print(data.head(10))


df = data.copy()

df['bathrooms'] = pd.to_numeric(df['bathrooms'], errors='coerce').astype('Int64')
df['bedrooms'] = pd.to_numeric(df['bedrooms'], errors='coerce').astype('Int64')
df['addedOn'] = pd.to_datetime(df['addedOn'], errors='coerce')
df['type'] = df['type'].astype('category')  # Only one unique value
df['price'] = pd.to_numeric(df['price'], errors='coerce')  # Assuming already numeric
df['verified'] = df['verified'].astype('boolean')
df['priceDuration'] = df['priceDuration'].astype('category')  # Only one unique value
df['sizeMin'] = pd.to_numeric(df['sizeMin'], errors='coerce')  # Likely numeric
df['furnishing'] = df['furnishing'].astype('category')  # 3 values: YES, NO, PARTLY
df['description'] = df['description'].astype('string')  # Free-text column




sdf = SmartDataframe(df, config={"llm": llm})
response = sdf.chat("Show properties in blue water")
print(type(response))
print(response)

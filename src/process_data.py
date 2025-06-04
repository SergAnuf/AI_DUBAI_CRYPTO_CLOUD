import pandas as pd

def change_data_type(data):
    
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
    df["displayAddress"] = df["displayAddress"].astype("string")  # Free-text column
    df['addedOn'] = df['addedOn'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    df["title"] = df["title"].astype("string")  # Free-text column
    df["City"] = df["displayAddress"].apply(lambda x: x.split(",")[-1].strip()) # add city column
    
    return df
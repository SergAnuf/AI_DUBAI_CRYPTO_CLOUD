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
    
    return df
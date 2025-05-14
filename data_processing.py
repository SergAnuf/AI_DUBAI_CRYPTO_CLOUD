import pandas as pd

def load_and_preprocess_data(filepath):
    """
    Load and preprocess the real estate data
    """
    data = pd.read_csv(filepath)
    
    # Data cleaning
    df = data.copy()
    df['bathrooms'] = pd.to_numeric(df['bathrooms'], errors='coerce').astype('Int64')
    df['bedrooms'] = pd.to_numeric(df['bedrooms'], errors='coerce').astype('Int64')
    df['addedOn'] = pd.to_datetime(df['addedOn'], errors='coerce')
    df['type'] = df['type'].astype('category')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['verified'] = df['verified'].astype('boolean')
    df['priceDuration'] = df['priceDuration'].astype('category')
    df['sizeMin'] = pd.to_numeric(df['sizeMin'], errors='coerce')
    df['furnishing'] = df['furnishing'].astype('category')
    df['description'] = df['description'].astype('string')
    
    return df
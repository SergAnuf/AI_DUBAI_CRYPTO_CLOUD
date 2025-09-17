import pandas as pd


class ListingAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def avg_price_per_bedroom(self) -> pd.DataFrame:
        return self.df.groupby('bedrooms', as_index=False)['price'].mean().rename(columns={'price': 'avg_price'})

    def count_by_type(self) -> pd.DataFrame:
        return self.df.groupby('type', as_index=False).size().rename(columns={'size': 'count'})

    def listing_date_range(self) -> pd.DataFrame:
        return pd.DataFrame({
            'min_date': [self.df['addedOn'].min()],
            'max_date': [self.df['addedOn'].max()]
        })

    def missing_size_count(self) -> pd.DataFrame:
        count = self.df['sizeMin'].isnull().sum()
        return pd.DataFrame({'missing_sizeMin_count': [count]})

    def price_per_sqm(self) -> pd.DataFrame:
        df = self.df.copy()
        df = df[df['sizeMin'] > 0]
        df['price_per_sqm'] = df['price'] / df['sizeMin']
        return df[['title', 'price', 'sizeMin', 'price_per_sqm']]

    def furnishing_distribution(self) -> pd.DataFrame:
        furnishing_counts = self.df['furnishing'].value_counts(normalize=True).reset_index()
        furnishing_counts.columns = ['furnishing', 'percentage']
        return furnishing_counts

    def top5_verified_expensive(self) -> pd.DataFrame:
        filtered = self.df[self.df['verified'] == True].sort_values(by='price', ascending=False).head(5)
        return filtered[['title', 'price', 'verified']]

    def price_duration_counts(self) -> pd.DataFrame:
        return self.df.groupby('priceDuration', as_index=False).size().rename(columns={'size': 'count'})

# resale_hdb.py
import json
import re
import matplotlib.pyplot as plt
import pandas as pd
from hdb_data_loader import HDBDataLoader, filter_by_date
import os

# Configuration
DATASET_ID = 'd_8b84c4ee58e3cfc0ece0d773c8ca6abc'# Make sure to set this

# Find all numbers followed by time units (case-insensitive)
def convert_lease_to_years(lease_str):
    matches = re.findall(r'(\d+)\s*(year|month|yr|mo|y|m)s?', lease_str.lower())
    years = 0
    months = 0
    for value, unit in matches:
        if unit in ('year', 'yr', 'y'):
            years = int(value)
        elif unit in ('month', 'mo', 'm'):
            months = int(value)
    
    return years + (months / 12)

def main():
    # Initialize data loader
    loader = HDBDataLoader(DATASET_ID)
    
    # Get metadata (optional)
    metadata, columns = loader.get_metadata()
    #print("\nDataset Metadata:")
    #print(json.dumps(metadata, indent=2))
    #print("\nColumns:\n", list(columns['map'].values()))
    
    # Download and process data
    df = loader.download_file()
    filtered_df = filter_by_date(df).copy()
    
    # Now you can work with filtered_df
    #print(filtered_df.describe())
    #print(filtered_df.columns)

    """
    Research Question 1: To what extent does price change across districts?
    
    Q1: Which towns have the lowest median resale price per square meter (Resale Price / Floor Area Sqm) for 4- or 5-room flats, and do these towns correlate with older (but sufficient) remaining lease periods?
    """

#For each transaction, calculate price/sqm
    filtered_df.loc[:, 'price_per_sqm'] = filtered_df['resale_price'] / filtered_df['floor_area_sqm']
    #print(filtered_df['price_per_sqm'])

    #Filter for 4- or 5-room flats
    fourfive_filtered_df = filtered_df[filtered_df['flat_type'].isin(['4 ROOM', '5 ROOM'])].copy()
    #print(fourfive_filtered_df)
    
    #Group by Town and Flat Type
    #Compare against Remaining Lease
    fourfive_filtered_df['remaining_lease_years'] = fourfive_filtered_df['remaining_lease'].apply(convert_lease_to_years)
    grouped = fourfive_filtered_df.groupby(['town', 'flat_type']).agg(   
        Median_Price_per_Sqm=('price_per_sqm', 'median'),
        Median_Remaining_Lease=('remaining_lease_years', 'median')
        ).reset_index()
    #print(grouped)

    sorted_grouped_price = grouped.sort_values(by='Median_Price_per_Sqm', ascending=True)
    sorted_grouped_lease = grouped.sort_values(by='Median_Remaining_Lease', ascending=True)
    #print(sorted_grouped_price, sorted_grouped_lease)

    def tabulate_monthly_price_variance(fourfive_filtered_df):

        # Convert 'month' column to datetime
        fourfive_filtered_df['month'] = pd.to_datetime(fourfive_filtered_df['month'])

        # Create 'year_month' column for grouping
        fourfive_filtered_df['year_month'] = fourfive_filtered_df['month'].dt.to_period('M')
        
        # Group by town and year_month and calculate variance
        variance_table = fourfive_filtered_df.groupby(['town', 'year_month']).agg(
            Price_Variance=('price_per_sqm', 'var'),
            Price_Std_Dev=('price_per_sqm', 'std'),
            Median_Price_per_Sqm=('price_per_sqm', 'median'),
            Min_Price_per_Sqm=('price_per_sqm', 'min'),
            Max_Price_per_Sqm=('price_per_sqm', 'max'),
            Count=('price_per_sqm', 'count')
        ).reset_index()

       # Optional: Convert year_month to string for cleaner export/view
        variance_table['year_month'] = variance_table['year_month'].astype(str)

        # Display or save as CSV
        print(variance_table)

        # Optionally, save to CSV
        print("Current Working Directory:", os.getcwd())
        variance_table.to_csv('town_monthly_price_variance.csv', index=False)
        
        return variance_table

    tabulate_monthly_price_variance(fourfive_filtered_df)

    

if __name__ == "__main__":
    main()
# resale_hdb.py
import json
import re
import matplotlib.pyplot as plt
import pandas as pd
from hdb_data_loader import HDBDataLoader, filter_by_date

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

    """
    ##chart this data
    def plot_remaining_lease_vs_price():
        plt.figure(figsize=(10, 6))
        plt.scatter(grouped['Median_Remaining_Lease'], grouped['Median_Price_per_Sqm'], alpha=0.7)
        
        for i, row in grouped.iterrows():
                plt.annotate(f"{row['town']}, {row['flat_type']}", 
                            (row['Median_Remaining_Lease'], row['Median_Price_per_Sqm']),
                            textcoords="offset points",  # how to position the text
                            xytext=(0,10),  # distance from text to points (x,y)
                            ha='center')  # horizontal alignment can be left, right or center

        plt.title('Median Price per Sqm vs. Median Remaining Lease')
        plt.xlabel('Median Remaining Lease (years)')
        plt.ylabel('Median Price per Sqm')
        plt.grid(True)
        plt.show()

    plot_remaining_lease_vs_price() """
    

    """
    Research Question 1: To what extent does price change across districts?
    
    Q2: How do prices across towns change month on month, across my pre-set date range?
    """

    def plot_median_price_per_sqm_by_town_month(fourfive_filtered_df, towns_to_include):
        # Filter the DataFrame to include only the specified towns
        filtered_towns_df = fourfive_filtered_df[fourfive_filtered_df['town'].isin(towns_to_include)]

        # Ensure the 'month' column is in datetime format
        filtered_towns_df['month'] = pd.to_datetime(filtered_towns_df['month'])

        # Extract month and year from the date
        filtered_towns_df['year_month'] = filtered_towns_df['month'].dt.to_period('M')

        # Group by town and year_month, then calculate the median price per sqm
        monthly_grouped = filtered_towns_df.groupby(['town', 'year_month']).agg(
            Median_Price_per_Sqm=('price_per_sqm', 'median')
        ).reset_index()

        # Plot the data
        plt.figure(figsize=(12, 8))
        for town in monthly_grouped['town'].unique():
            town_data = monthly_grouped[monthly_grouped['town'] == town]
            plt.plot(
                town_data['year_month'].astype(str), 
                town_data['Median_Price_per_Sqm'], 
                label=town,
                linewidth=1,
            )

        plt.title('Median Price per Sqm by Town Each Month')
        plt.xlabel('Month')
        plt.ylabel('Median Price per Sqm')
        plt.xticks(rotation=45)
        plt.legend(loc='upper right')
        plt.grid(False)
        plt.tight_layout()
        plt.show()

    towns_to_include = ['GEYLANG']

    plot_median_price_per_sqm_by_town_month(fourfive_filtered_df, towns_to_include)
    

if __name__ == "__main__":
    main()
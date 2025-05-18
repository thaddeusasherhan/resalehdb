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

def generate_town_script(town_name, df):
    # Create a new Python file for this town
    filename = f"resale_hdb_{town_name.lower().replace('/', '_').replace(' ', '_')}.py"
    
    with open(filename, 'w') as f:
        f.write(f"""# Analysis for {town_name}
import pandas as pd
import matplotlib.pyplot as plt

def analyze_town_data(df, town_name='{town_name}'):
    # Filter data for this specific town
    town_df = df[df['town'] == town_name].copy()
    
    # Ensure the 'month' column is in datetime format
    town_df['month'] = pd.to_datetime(town_df['month'])

    # Extract month and year from the date as a period
    town_df['year_month'] = town_df['month'].dt.to_period('M')
    
    # Group by year_month and compute statistics
    grouped = town_df.groupby('year_month').agg(
        Min_Price_per_Sqm=('price_per_sqm', 'min'),
        Max_Price_per_Sqm=('price_per_sqm', 'max'),
        Median_Price_per_Sqm=('price_per_sqm', 'median'),
        Price_Variance=('price_per_sqm', 'var'),
        Price_Std=('price_per_sqm', 'std')
    ).reset_index()

    # Convert year_month (Period) to string for x-axis labels
    grouped['year_month_str'] = grouped['year_month'].astype(str)

    # Create the plot
    plt.figure(figsize=(12, 8))
    
    # For every group (each month), draw a vertical line from min to max
    for _, row in grouped.iterrows():
        # Plot vertical line from min to max
        plt.vlines(x=row['year_month_str'], 
                ymin=row['Min_Price_per_Sqm'], 
                ymax=row['Max_Price_per_Sqm'], 
                colors='blue', 
                lw=2)
        
        # Plot median
        plt.plot(row['year_month_str'], row['Median_Price_per_Sqm'],
                marker='o', color='red', markersize=8)

        # Plot error bars
        plt.errorbar(
            x=row['year_month_str'],
            y=row['Median_Price_per_Sqm'],
            yerr=row['Price_Std'],
            fmt='o',
            color='green',
            ecolor='lightgreen',
            elinewidth=2,
            capsize=4
        )

    plt.title(f'Price per Sqm Range with Median by Month - {town_name}')
    plt.xlabel('Month')
    plt.ylabel('Price per Sqm')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{town_name.lower().replace('/', '_').replace(' ', '_')}_analysis.png")
    plt.close()

if __name__ == "__main__":
    # Load the main dataframe - you'll need to modify this path
    from resale_hdb_var import HDBDataLoader, filter_by_date, DATASET_ID
    
    loader = HDBDataLoader(DATASET_ID)
    df = loader.download_file()
    filtered_df = filter_by_date(df).copy()
    
    # Calculate price per sqm
    filtered_df['price_per_sqm'] = filtered_df['resale_price'] / filtered_df['floor_area_sqm']
    
    # Filter for 4- or 5-room flats
    fourfive_filtered_df = filtered_df[filtered_df['flat_type'].isin(['4 ROOM', '5 ROOM'])].copy()
    
    # Analyze data for this town
    analyze_town_data(fourfive_filtered_df)
""")

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

    def plot_min_max_price_per_sqm_by_town_month(fourfive_filtered_df, towns_to_include):
    # Filter the DataFrame to include only the specified towns
        filtered_towns_df = fourfive_filtered_df[fourfive_filtered_df['town'].isin(towns_to_include)].copy()

        # Ensure the 'month' column is in datetime format
        filtered_towns_df['month'] = pd.to_datetime(filtered_towns_df['month'])

        # Extract month and year from the date as a period
        filtered_towns_df['year_month'] = filtered_towns_df['month'].dt.to_period('M')
        
        # Group by year_month and compute the minimum and maximum price per sqm
        grouped = filtered_towns_df.groupby('year_month').agg(
            Min_Price_per_Sqm=('price_per_sqm', 'min'),
            Max_Price_per_Sqm=('price_per_sqm', 'max'),
            Median_Price_per_Sqm=('price_per_sqm', 'median'),
            Price_Variance=('price_per_sqm', 'var'),
            Price_Std=('price_per_sqm', 'std')
        ).reset_index()

        # Convert year_month (Period) to string for x-axis labels
        grouped['year_month_str'] = grouped['year_month'].astype(str)

        # Create the plot
        plt.figure(figsize=(12, 8))
        
        # For every group (each month), draw a vertical line from min to max
        for _, row in grouped.iterrows():
            # Plot a vertical line from min to max for each month
            plt.vlines(x=row['year_month_str'], 
                    ymin=row['Min_Price_per_Sqm'], 
                    ymax=row['Max_Price_per_Sqm'], 
                    colors='blue', 
                    lw=2)
            
            # Plot the median as a red circular marker on top of the vertical line
            plt.plot(row['year_month_str'], row['Median_Price_per_Sqm'],
                    marker='o', color='red', markersize=8)

            # Plot an error bar representing ±1 std from the median
            plt.errorbar(
                    x=row['year_month_str'],
                    y=row['Median_Price_per_Sqm'],
                    yerr=row['Price_Std'],          # This is your standard deviation
                    fmt='o',                        # Marker type
                    color='green',                  # Marker color
                    ecolor='lightgreen',            # Error bar color
                    elinewidth=2,
                    capsize=4                       # Little horizontal strokes at the ends of error bars
                    )

        plt.title('Price per Sqm Range with Median by Month')
        plt.xlabel('Month')
        plt.ylabel('Price per Sqm')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    # Example usage:
    towns_to_include = ['ANG MO KIO', 'BEDOK', 'BISHAN', 'BUKIT BATOK', 'BUKIT MERAH', 'BUKIT PANJANG', 'BUKIT TIMAH', 'CENTRAL AREA', 'CHOA CHU KANG', 'CLEMENTI', 'GEYLANG', 'HOUGANG', 'JURONG EAST', 'JURONG WEST', 'KALLANG/WHAMPOA', 'MARINE PARADE', 'PASIR RIS', 'PUNGGOL', 'QUEENSTOWN', 'SENGKANG', 'SEMBAWANG', 'SERANGOON', 'TAMPINES', 'TOA PAYOH', 'WOODLANDS', 'YISHUN']
    
    for town in towns_to_include:
        generate_town_script(town, fourfive_filtered_df)
        plot_min_max_price_per_sqm_by_town_month(fourfive_filtered_df, towns_to_include)

    

if __name__ == "__main__":
    main()
# Analysis for PUNGGOL
import pandas as pd
import matplotlib.pyplot as plt

def analyze_town_data(df, town_name='PUNGGOL'):
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
    fig = plt.figure(figsize=(12, 8))
    
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

    plt.title(f'Price per Sqm Range with Median by Month - PUNGGOL')
    plt.xlabel('Month')
    plt.ylabel('Price per Sqm')
    plt.xticks(rotation=45)
    plt.tight_layout()

    return fig
    #plt.savefig(f"punggol_analysis.png")
    #plt.close()

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

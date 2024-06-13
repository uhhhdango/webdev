import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

def analyze_monthly_mean_temperature(files, start_year, end_year, target_latitude, target_longitude):
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    for file_path in files:
        # Extract data source name from the file name
        data_source = os.path.basename(file_path).split('_')[1].split('.')[0].upper()
        # Load the data
        df = pd.read_csv(file_path)
        df['time'] = pd.to_datetime(df['time'])
        df['month'] = df['time'].dt.month
        df['year'] = df['time'].dt.year
        # Find the closest latitude and longitude values to the target
        closest_latitude = df['latitude'].iloc[(df['latitude'] - target_latitude).abs().argsort()[:1]].values[0]
        closest_longitude = df['longitude'].iloc[(df['longitude'] - target_longitude).abs().argsort()[:1]].values[0]
        # Filter data for the specified years and closest location
        df_filtered = df[(df['year'] >= start_year) & (df['year'] <= end_year) & 
                         (df['latitude'] == closest_latitude) & (df['longitude'] == closest_longitude)]
        temp_column = 'temperature'
        # Calculate the monthly mean temperature for each year
        monthly_mean = df_filtered.groupby(['year', 'month'])[temp_column].mean().reset_index()
        # Calculate the overall monthly mean temperature across all years
        overall_monthly_mean = monthly_mean.groupby('month')[temp_column].mean().reset_index()
        # Plot the overall monthly mean temperature as a column chart
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(overall_monthly_mean['month'], overall_monthly_mean[temp_column], color='#87CEEB', label=f'{start_year}-{end_year}', width=0.4, zorder=3)
        ax.set_xlabel('Month')
        ax.set_ylabel('Average Temperature (°C)')
        ax.set_title(f'Average Monthly Temperature (Lat: {closest_latitude}, Lon: {closest_longitude}) - from {start_year} to {end_year} - {data_source} through COD')
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(month_names)
        ax.set_ylim(0, 40)  
        ax.grid(axis='y', linestyle='-', linewidth=0.7, zorder=0)
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2.0, height, f'{height:.1f}', ha='center', va='bottom', fontsize=10)
        plt.tight_layout()
        # Save the plot
        save_plot(fig, f'{data_source}_average_monthly_temperature_{closest_latitude}_{closest_longitude}_{start_year}_{end_year}.png')
def save_plot(fig, file_name):
    results_dir = 'results'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    file_path = os.path.join(results_dir, file_name)
    fig.savefig(file_path)
    plt.close(fig)
# Input files and years range
files = ['X:\webdev\ocean_data_website\cod_cmems_data.csv']
start_year = 1993
end_year = 2023
target_latitude = 20
target_longitude = 107
# Analyze and plot the data
analyze_monthly_mean_temperature(files, start_year, end_year, target_latitude, target_longitude)

import cdsapi
import psycopg2
import pandas as pd
from tqdm import tqdm
from django.core.management.base import BaseCommand

def retrieve_era5_data(start_year, end_year):
    c = cdsapi.Client()

    # Generate a list of years from start_year to end_year
    years = [str(year) for year in range(start_year, end_year + 1)]

    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type': 'reanalysis',
            'variable': ['sea_surface_temperature'],
            'year': years,
            'month': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'],
            'day': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31'],
            'time': ['00:00'],
            'area': [20.1, 107, 20, 107.1,],
            'format': 'netcdf'
        },
        'era5_data.nc')  # Output file name

class Command(BaseCommand):
    help = 'Insert ERA5 data from CSV into PostgreSQL database'

    def handle(self, *args, **kwargs):
        # Database connection details
        DB_NAME = 'oceandb'
        DB_USER = 'hai'
        DB_PASSWORD = 'dango123'
        DB_HOST = 'localhost'
        DB_PORT = '5432'

        print("Connecting to the database...")
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        print("Successfully connected to the database.")

        print("Reading data from CSV file...")
        # Read data from CSV
        df = pd.read_csv('.\era5_data.csv')
        print(f"Successfully read {len(df)} records from the CSV file.")

        # Prepare data for batch insert
        print("Preparing data for batch insertion...")
        data_tuples = []

        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Preparing data"):
            source = 'ERA5'
            latitude = row['latitude']
            longitude = row['longitude']
            time = pd.to_datetime(row['time'])  # Ensure time is correctly formatted
            depth = 0  # Assuming depth is not provided in ERA5 data, setting to 0 or appropriate default
            temperature = row['sst']  # Temperature in Celsius
            salinity = None  # Assuming salinity data is not available

            if pd.isna(temperature):
                continue

            data_tuples.append((
                source,
                latitude,
                longitude,
                time,
                depth,
                temperature,
                salinity
            ))
        print("Data preparation complete.")

        # Define the insert query with ON CONFLICT clause
        insert_query = """
            INSERT INTO main_oceandata (source, latitude, longitude, time, depth, temperature, salinity)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (source, latitude, longitude, time) 
            DO UPDATE SET depth = EXCLUDED.depth, temperature = EXCLUDED.temperature, salinity = EXCLUDED.salinity
        """

        # Use psycopg2's execute_batch for efficient batch insertion
        from psycopg2.extras import execute_batch

        # Insert data with a progress bar
        batch_size = 1000  # Adjust batch size as needed
        total_batches = len(data_tuples) // batch_size + (1 if len(data_tuples) % batch_size else 0)

        print("Starting batch insertion...")
        with tqdm(total=total_batches, desc="Inserting data") as pbar:
            for i in range(0, len(data_tuples), batch_size):
                batch = data_tuples[i:i + batch_size]
                execute_batch(cur, insert_query, batch)
                conn.commit()
                pbar.update(1)
        print("Batch insertion complete.")

        # Close the cursor and connection
        cur.close()
        conn.close()
        print("Database connection closed.")
        print("Data successfully inserted into PostgreSQL.")

# Specify the range of years
start_year = 2020
end_year = 2023

# Retrieve ERA5 data
retrieve_era5_data(start_year, end_year)

# Insert data into the PostgreSQL database
command = Command()
command.handle()

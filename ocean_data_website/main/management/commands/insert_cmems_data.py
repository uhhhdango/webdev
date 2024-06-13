import psycopg2
import pandas as pd
import json
from tqdm import tqdm
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Insert CMEMS data from CSV into PostgreSQL database'

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

        # Read the latest CMEMS configuration
        with open('latest_cmems_config.json', 'r') as config_file:
            config = json.load(config_file)
            variables = config["variables"]
            filename = config["filename"]

        print(f"Reading data from CSV file {filename}...")
        # Read data from CSV
        df = pd.read_csv(filename)
        print(f"Successfully read {len(df)} records from the CSV file.")

        # Determine if temperature and/or salinity are present
        has_temperature = 'thetao' in df.columns
        has_salinity = 'so' in df.columns

        # Prepare data for batch insert
        print("Preparing data for batch insertion...")
        data_tuples = []

        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Preparing data"):
            source = 'CMEMS'
            latitude = row['latitude']
            longitude = row['longitude']
            time = pd.to_datetime(row['time'])  # Ensure time is correctly formatted
            depth = row.get('depth', 0)
            temperature = row['thetao'] if has_temperature else None
            salinity = row['so'] if has_salinity else None

            # Skip rows where both temperature and salinity are NaN
            if pd.isna(temperature) and pd.isna(salinity):
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

        # Define the insert query with conflict resolution
        insert_query = """
            INSERT INTO main_oceandata (source, latitude, longitude, time, depth, temperature, salinity)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (source, latitude, longitude, time) DO UPDATE
            SET depth = EXCLUDED.depth,
                temperature = EXCLUDED.temperature,
                salinity = EXCLUDED.salinity
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

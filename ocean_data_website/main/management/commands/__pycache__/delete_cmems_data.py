import psycopg2
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Delete all CMEMS data from PostgreSQL database'

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

        # Define the delete query
        delete_query = "DELETE FROM main_oceandata WHERE source = 'CMEMS'"

        try:
            # Execute the delete query
            cur.execute(delete_query)
            conn.commit()
            print("Successfully deleted all CMEMS data from the database.")
        except Exception as e:
            print(f"An error occurred: {e}")
            conn.rollback()
        
        # Close the cursor and connection
        cur.close()
        conn.close()
        print("Database connection closed.")

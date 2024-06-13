import pandas as pd

# Load the CSV file
file_path = 'X:\webdev\ocean_data_website\cmems_data.csv'
df = pd.read_csv(file_path)

# Display the column names and the first few rows
print(df.columns)
print(df.head())

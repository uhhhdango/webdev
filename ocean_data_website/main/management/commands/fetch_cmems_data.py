import copernicusmarine as cm
from django.core.management.base import BaseCommand
import pandas as pd
import xarray as xr
import json
import os

class Command(BaseCommand):
    help = 'Fetch CMEMS data'

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write(self.style.NOTICE('Fetching data from CMEMS...'))

            # Paste the copied code from CMEMS here as a multiline string
            cmems_parameters = """
            dataset_id="cmems_mod_glo_phy_my_0.083deg_P1D-m",
            dataset_version="202311",
            variables=["thetao"],
            minimum_longitude=107,
            maximum_longitude=107,
            minimum_latitude=20,
            maximum_latitude=20,
            start_datetime="1993-01-01T00:00:00",
            end_datetime="2021-06-30T00:00:00",
            minimum_depth=0.49402499198913574,
            maximum_depth=0.49402499198913574,
            """

            # Parse the pasted parameters
            parameters = {}
            for line in cmems_parameters.strip().splitlines():
                if line.strip():
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip(",")
                    if value.startswith("[") and value.endswith("]"):
                        value = eval(value)  # convert string representation of list to actual list
                    elif value.replace('.', '', 1).replace('-', '', 1).isdigit():
                        value = float(value) if '.' in value else int(value)
                    else:
                        value = value.strip('"').strip("'")
                    parameters[key] = value

            # Extract the parameters
            dataset_id = parameters["dataset_id"]
            dataset_version = parameters["dataset_version"]
            variables = parameters["variables"]
            minimum_longitude = parameters["minimum_longitude"]
            maximum_longitude = parameters["maximum_longitude"]
            minimum_latitude = parameters["minimum_latitude"]
            maximum_latitude = parameters["maximum_latitude"]
            start_datetime = parameters["start_datetime"]
            end_datetime = parameters["end_datetime"]
            minimum_depth = parameters["minimum_depth"]
            maximum_depth = parameters["maximum_depth"]
            username = "elyris"
            password = "Kobie123"

            # Construct the filename for the original data file
            filename_nc = (
                f"{dataset_id}_{'_'.join(variables)}_{minimum_longitude:.2f}E-{maximum_longitude:.2f}E_"
                f"{minimum_latitude:.2f}N-{maximum_latitude:.2f}N_{minimum_depth:.2f}m_{start_datetime[:10]}-"
                f"{end_datetime[:10]}.nc"
            ).replace("--", "-")

            # Remove any existing .nc file with the same name
            if os.path.exists(filename_nc):
                os.remove(filename_nc)
                self.stdout.write(self.style.NOTICE(f'Removed existing file: {filename_nc}'))

            # Fetch data from CMEMS
            dataset = cm.subset(
                dataset_id=dataset_id,
                dataset_version=dataset_version,
                variables=variables,
                minimum_longitude=minimum_longitude,
                maximum_longitude=maximum_longitude,
                minimum_latitude=minimum_latitude,
                maximum_latitude=maximum_latitude,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                minimum_depth=minimum_depth,
                maximum_depth=maximum_depth,
                username=username,
                password=password,
            )

            self.stdout.write(self.style.SUCCESS('Successfully fetched CMEMS data'))

            # Convert the dataset to a pandas DataFrame
            ds = xr.open_dataset(dataset)
            df = ds.to_dataframe().reset_index()

            # Create a filename based on the variables
            variable_names = "_".join(variables)
            filename_csv = f'cmems_data_{variable_names}.csv'

            # Save the DataFrame as a CSV file
            df.to_csv(filename_csv, index=False)
            self.stdout.write(self.style.SUCCESS(f'Successfully saved CMEMS data to {filename_csv}'))

            # Save the variable names to a configuration file
            with open('latest_cmems_config.json', 'w') as config_file:
                json.dump({"variables": variables, "filename": filename_csv}, config_file)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error fetching CMEMS data: {e}'))

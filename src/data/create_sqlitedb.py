import os
import sys
import pandas as pd
from re import sub
from sqlalchemy import create_engine

# Create paths to data folders
print("Setting file paths...")

# Create a variable for the project root directory
#proj_root = os.path.join(os.pardir)
proj_root = os.path.join(os.pardir, os.pardir)

# Save the path to the folder containing the original, immutable data dump:
# /data/raw/instacart_2017_05_01
raw_data_dir = os.path.join(proj_root,
                                "data",
                                "raw",
                                "instacart_2017_05_01")

# Save the path to the folder that will contain the intermediate data 
# that will be transformed: /data/interim
interim_data_dir = os.path.join(proj_root,
                                "data",
                                "interim")

# Save the path to the SQLite databse we will create in /data/interim
db_name = 'instacart_2017_05_01.db'

interim_sqlitedb = os.path.join('sqlite:///',
                                interim_data_dir,
                                db_name)

# Put the contents of csv files into a sqlite database
print("Building SQLite database...")

# Create list of data files
raw_data_files = os.listdir(raw_data_dir)

# Create list of table names
table_names = [sub('.csv', '', fn) for fn in raw_data_files]

# Create a sqllite database
engine = create_engine(interim_sqlitedb)

# Set the chunksize to 100,000 to keep the size of the chunks managable.
chunksize = 100000

# Iterate over each csv file in chunks and store the data 
# from each csv file in its own table in the sqllite database

for i in range(len(raw_data_files)):

    print("Building {} table...".format(table_names[i]))

    file_dir = os.path.join(raw_data_dir, raw_data_files[i])
    
    # Initialize iterator variables
    j = 1

    # Set the table name
    table_name = sub('.csv', '', raw_data_files[i])
    
    for df in pd.read_csv(file_dir, chunksize=chunksize, iterator=True):
        # Make sure column names won't contain spaces.
        df = df.rename(columns={c: c.replace(' ', '_') for c in df.columns})
        # Set index values and table values
        df.index += j
        df.to_sql(table_name, engine, if_exists='append')
        j = df.index[-1] + 1

print("Finished! The SQLite database has been built")

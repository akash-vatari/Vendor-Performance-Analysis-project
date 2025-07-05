import pandas as pd
import os
from sqlalchemy import create_engine
import logging
import time

# Set up logging with corrected format string
logging.basicConfig(
    filename="logs/ingestion_db.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",  # FIXED typo here
    filemode="a"
)

# Create SQLAlchemy engine
engine = create_engine('sqlite:///inventoty.db')  # Note: Consider correcting the filename if "inventoty.db" is a typo for "inventory.db"

def ingest_db(df, table_name, engine):
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)

def load_raw_data():
    # This function will load CSVs as DataFrames and ingest them into the database
    start = time.time()
    for file in os.listdir('data'):
        if file.endswith('.csv'):  # Optional: Filter only CSV files
            df = pd.read_csv(os.path.join('data', file))
            logging.info(f'Ingesting {file} into db')
            ingest_db(df, file[:-4], engine)
    end = time.time()
    total_time = (end - start) / 60
    logging.info('-----------Ingestion complete-----------')
    logging.info(f'Total time taken: {total_time:.2f} minutes')

if __name__ == '__main__':
    load_raw_data()
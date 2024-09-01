import streamlit as st
import pandas as pd
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for file paths
TESTS_UNLOAD_CSV_FILE_PATH = 'Data/TestUnload.csv'  # Adjust the path if necessary

def read_csv_file(filename):
    """Read data from a CSV file."""
    try:
        df = pd.read_csv(filename)
        logger.info(f"Successfully loaded data from {filename}")
        return df
    except FileNotFoundError:
        st.error(f"File not found: {filename}")
        logger.error(f"File not found: {filename}")
        return pd.DataFrame()
    except pd.errors.EmptyDataError:
        st.error(f"No data: The file {filename} is empty.")
        logger.error(f"No data: The file {filename} is empty.")
        return pd.DataFrame()
    except pd.errors.ParserError:
        st.error(f"Parsing error: The file {filename} is corrupt or has an invalid format.")
        logger.error(f"Parsing error: The file {filename} is corrupt or has an invalid format.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        logger.exception("Unexpected error occurred while reading the CSV file.")
        return pd.DataFrame()
    

st.title('Back up data')
st.write('This is a page to download all data from host')

data = read_csv_file(TESTS_UNLOAD_CSV_FILE_PATH)
st.write("Columns in the file:", data.columns.values)
st.write(data)

# Set the directory where your CSV files are stored
folder_path = "Data"  # Change this to your CSV directory path

# Loop through each file in the directory
for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        file_path = os.path.join(folder_path, filename)

        # Read the file contents
        with open(file_path, "rb") as file:
            file_bytes = file.read()

        # Create a download button for each file
        st.download_button(
            label=f"Download {filename}",
            data=file_bytes,
            file_name=filename,
            mime="text/csv"
        )
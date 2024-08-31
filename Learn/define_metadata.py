import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for file paths
TESTS_CSV_FILE_PATH = 'Data/TestsList.csv'
USERDATA_CSV_FILE_PATH = 'Data/UserData.csv'
CLASSDATA_CSV_FILE_PATH = 'Data/ClassData.csv'
ATTEMPTDATA_CSV_FILE_PATH = 'Data/AttemptData.csv'
PLACEHOLDER_IMAGE = "Data/image/placeholder_image.png"
IMAGE_SIZE = 140  # Set this to the desired thumbnail size

@st.cache_data
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

@st.cache_data
def fetch_and_resize_image(url, size):
    """Fetch an image from a URL and resize it to the given size."""
    try:
        response = requests.get(url, timeout=5)
        img = Image.open(BytesIO(response.content))
        img.thumbnail((size, size))
        logger.info(f"Image fetched and resized from {url}")
        return img
    except requests.RequestException as e:
        logger.error(f"Error fetching image from {url}: {e}")
        return Image.open(PLACEHOLDER_IMAGE).resize((size, size))
    except Exception as e:
        logger.error(f"Error processing image from {url}: {e}")
        return Image.open(PLACEHOLDER_IMAGE).resize((size, size))

def main_define_metadata():
    """Show the editor for a specific TestID."""
    selected_test = st.session_state.get("selected_test")
    if not selected_test:
        st.write("No TestID selected.")
        return

    test_id = selected_test

    """Main function to display pretest form."""
    st.title("Pre-Test")

    # Load CSV data with caching
    df_test = read_csv_file(TESTS_CSV_FILE_PATH)
    df_user = read_csv_file(USERDATA_CSV_FILE_PATH)
    df_class = read_csv_file(CLASSDATA_CSV_FILE_PATH)
    df_attempt = read_csv_file(ATTEMPTDATA_CSV_FILE_PATH)

    # Filter the DataFrame for the selected TestID in TestsList.csv
    test_info = df_test[df_test['TestID'] == int(test_id)]
    if test_info.empty:
        st.write(f"No data found for TestID {test_id} in TestsList.csv")
    else:
        # Displaying a sample of the data for confirmation
        st.write(f"### {int(test_id)} - {test_info['TestName'].values[0]} (Language: {test_info['TestLanguage'].values[0]})")
        st.dataframe(test_info)

        # You can also include a form or further actions here
        st.write("Form or additional data processing can be included here.")
    
    if st.button("🔙 Back"):
        st.session_state.page = 'test_list'
        st.session_state.selected_test = None
        st.rerun()

# Run the main function
main_define_metadata()

import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import logging
from Do_Test.define_metadata import main_define_metadata

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for file paths
TESTS_CSV_FILE_PATH = 'data/TestsList.csv'  # Adjust the path if necessary
PLACEHOLDER_IMAGE = "data/image/placeholder_image.png"
IMAGE_SIZE = 60  # Set this to the desired thumbnail size (e.g., 60 pixels)

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
        return img
    except requests.RequestException as e:
        logger.error(f"Error fetching image from {url}: {e}")
        return Image.open(PLACEHOLDER_IMAGE).resize((size, size))
    except Exception as e:
        logger.error(f"Error processing image from {url}: {e}")
        return Image.open(PLACEHOLDER_IMAGE).resize((size, size))

def show_test_list(df):
    st.write("### Select your test")

    # Define custom CSS styles for minor visual tweaks
    # st.markdown("""
    #     <style>
    #     .stButton > button {
    #         border-radius: 5px;
    #         background-color: #4CAF50;
    #         color: white;
    #         padding: 5px 10px;
    #         font-size: 12px;
    #         margin: 0;
    #     }
    #     .stButton > button:hover {
    #         background-color: #45a049;
    #     }
    #     .image-cell img {
    #         display: block;
    #         margin-left: auto;
    #         margin-right: auto;
    #     }
    #     </style>
    # """, unsafe_allow_html=True)

    for index, row in df.iterrows():
        cols = st.columns([1, 2, 1, 2, 1])  # Adjust column widths

        # Check if the image URL is valid; if not, use the placeholder image
        image_url = row["Image"]
        img = fetch_and_resize_image(image_url if image_url else PLACEHOLDER_IMAGE, IMAGE_SIZE)

        # Display row data with improved layout
        cols[0].image(img)
        cols[1].write(row["TestName"])
        cols[2].write(row["TestLanguage"])
        cols[3].write(row["TestDescription"])

        # Add button to the last column and handle click
        if cols[4].button('Do Test', key=f"button_{index}"):
            st.session_state.selected_test = row['TestID']
            st.session_state.page = 'prep_test'
            st.rerun()

def show_test_id(test_id):
    """Display the TestID in a pop-up frame."""
    st.write(f"**TestID:** {test_id}")

def main_show_test_list():
    """Main function to display the test list page."""
    
    if 'page' not in st.session_state:
        st.session_state.page = 'test_list'
    if 'selected_test' not in st.session_state:
        st.session_state.selected_test = None

    #"""Page routing logic."""
    if st.session_state.page == 'test_list':
        st.title("Test List")
        # Load and display the test list
        df = read_csv_file(TESTS_CSV_FILE_PATH)
        if not df.empty:
            show_test_list(df)
        else:
            st.write("No data available.")
    elif st.session_state.page == 'prep_test':
            main_define_metadata()

main_show_test_list()

import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import logging
from PIL import Image
import random
from gtts import gTTS
import tempfile

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for file paths
TESTS_CSV_FILE_PATH = 'data/TestsList.csv'
WORDS_CSV_FILE_PATH = 'data/WordsList.csv'
ATTEMPTDATA_CSV_FILE_PATH = 'data/AttemptData.csv'
PLACEHOLDER_IMAGE = "data/image/placeholder_image.png"
IMAGE_SIZE = 150  # Set this to the desired thumbnail size

st.markdown(
    """
    <style>
    .center-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def read_csv_file(filename):
    """Read data from a CSV file."""
    try:
        df = pd.read_csv(filename)
        logger.info(f"Successfully loaded data from {filename}")
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError) as e:
        st.error(f"Error loading file: {filename} - {str(e)}")
        logger.error(f"Error loading file: {filename} - {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        logger.exception(f"Unexpected error occurred while reading the CSV file.")
        return pd.DataFrame()

def get_filtered_words(test_id):
    """Read and filter the WordsList.csv file based on the TestID."""
    try:
        df_words = read_csv_file(WORDS_CSV_FILE_PATH)
        filtered_words = df_words[df_words['TestID'] == int(test_id)]
        return filtered_words  # Return the filtered DataFrame
    except Exception as e:
        st.error(f"Error filtering WordsList.csv: {e}")
        return pd.DataFrame()

def set_words_order(df, order_type):
    number_of_rows = len(df) 
    if order_type == "sequence":
        order = list(range(1, number_of_rows + 1)) # Create a sequence list from 1 to number_of_rows
    elif order_type == "random":
        order = random.sample(range(1, number_of_rows + 1), number_of_rows) # Create a random list from 1 to number_of_rows without duplicates
    else:
        order = list(range(1, number_of_rows + 1))
        st.warning("Invalid order_type. Must be 'sequence' or 'random'. return default order is 'sequence'")
    df.insert(0, 'order', order)
    return df

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

# Define a function to display data of the current row
def display_current_row(df, order_number):
    current_row_data = df[df['order']== order_number]  # -1 because order is 1-based
    
    col1, col2 = st.columns([8, 2])
    with col1:
        st.markdown('<div class="center-container">', unsafe_allow_html=True)
        status_container = st.container(height=220) 
        def update_status(new_status):
            with status_container:
                
                if new_status == True:
                    # Check if the image URL is valid; if not, use the placeholder image
                    image_url = current_row_data["Image"].iloc[0]
                    st.image(fetch_and_resize_image(image_url if image_url else PLACEHOLDER_IMAGE, IMAGE_SIZE))
                if new_status == False:
                    st.write("Show Word")
                    st.write(f"Word: {current_row_data['Word'].iloc[0]}")
                    st.write("Show WordPhonetic")
                
        # Initial status display
        update_status(st.session_state.show_image)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.write('----------------------')
        with st.container():
            st.write("Show Description")
            st.write("Show Input Textbox")
            st.write("Show UnderLine")
        st.write(current_row_data)
    with col2:
        st.subheader("Tools")
        if st.button("show"):
            st.session_state.show_image = not st.session_state.show_image
            st.rerun()
        st.button("hint")
        if st.button("speak"):
            #st.write(f"debug {current_row_data['Word'][0]}")
            word = current_row_data['Word'].iloc[0]
            lang_code = current_row_data['LanguageCode'].iloc[0]

            # Generate speech
            tts = gTTS(text = word, lang = lang_code)

            # Save the speech to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                tts.save(fp.name)
                st.audio(fp.name, format="audio/mp3", autoplay=True)
    
def footer_buttons():
    button_cols = st.columns([1, 2, 1])
    with button_cols[0]:
        if st.button("🔙 Back", key="do_test_back"):
            st.session_state.page = 'test_list'
            st.session_state.selected_test = None
            st.rerun()
    with button_cols[1]:
        st.write(" ")
    with button_cols[2]:
        if st.button("Submit", key="do_test_submit"):
            st.write("submit action")

def main_do_test():
    # Handle paging displaying session
    if st.session_state.page == 'do_test':
        selected_test = st.session_state.get("selected_test")
        if not selected_test:
            st.write("No TestID selected.")
            return
    else: 
        st.session_state.page == 'test_list'
        return
    
    # Initialize the current order | show image if it doesn't exist
    if 'word_index' not in st.session_state:
        st.session_state.word_index = 1 

    if 'show_image' not in st.session_state:
        st.session_state.show_image = True

    # Get the filtered words data base on TestID (selected_test) from WordsList.csv
    test_id = int(selected_test)
    df_test_words = get_filtered_words(test_id)
    df_test_words = set_words_order(df_test_words, order_type = "sequence") # order_type = "sequence"|"random"
    current_row_data = df_test_words[df_test_words['order']== st.session_state.word_index]
    
    st.title(f"Do Test - {test_id}")
    display_current_row(df_test_words,st.session_state.word_index)
    
    number_of_rows = len(df_test_words)
    
# Create a button to go to the next item
    if st.button(f'Next', disabled=(st.session_state.word_index >= number_of_rows)):
        if st.session_state.word_index < number_of_rows:
            st.session_state.word_index += 1
            st.session_state.show_image = True
            st.rerun()
    footer_buttons()
    
main_do_test()
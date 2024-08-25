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
TESTS_CSV_FILE_PATH = 'data/TestsList.csv'
USERDATA_CSV_FILE_PATH = 'data/UserData.csv'
CLASSDATA_CSV_FILE_PATH = 'data/ClassData.csv'
ATTEMPTDATA_CSV_FILE_PATH = 'data/AttemptData.csv'
PLACEHOLDER_IMAGE = "data/image/placeholder_image.png"
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

        # Create dropdowns for UserName and ClassName in two columns
        cols = st.columns([1, 1])
        with cols[0]:
            selected_user_name = st.selectbox("Select User", df_user['UserName'])
        with cols[1]:
            selected_class_name = st.selectbox("Select Class", df_class['ClassName'])

        # Add two buttons: "Do Test" and "Back"
        if st.button("Do Test"):
            # Find UserID and ClassID based on selections
            selected_user_id = df_user.loc[df_user['UserName'] == selected_user_name, 'UserID'].values[0]
            selected_class_id = df_class.loc[df_class['ClassName'] == selected_class_name, 'ClassID'].values[0]
            
            # Generate new AttemptID
            if df_attempt.empty:
                new_attempt_id = 1
            else:
                new_attempt_id = df_attempt['AttemptID'].max() + 1

            # Prepare new row for AttemptData
            new_attempt_data = {
                'AttemptID': [new_attempt_id],  # Ensure this is a list
                'UserID': [selected_user_id],  # Ensure this is a list
                'ClassID': [selected_class_id],  # Ensure this is a list
                'TestID': [test_id],  # Ensure this is a list
                'TotalQuestion': [''],  # Ensure this is a list
                'CorrectList': [''],  # Ensure this is a list
                'WrongList': ['']  # Ensure this is a list
            }

            # Debugging: Print new_attempt_data to verify structure
            #st.write(new_attempt_data)

            # Create a DataFrame for the new attempt data
            new_attempt_df = pd.DataFrame.from_dict(new_attempt_data)  # No need to specify index when using from_dict

            # Concatenate the new attempt data with the existing DataFrame
            df_attempt = pd.concat([df_attempt, new_attempt_df], ignore_index=True)
            df_attempt.to_csv(ATTEMPTDATA_CSV_FILE_PATH, index=False)
            st.success("Test attempt recorded successfully.")

        if st.button("🔙 Back"):
            st.session_state.page = 'test_list'
            st.session_state.selected_test = None
            st.rerun()

# Run the main function
main_define_metadata()

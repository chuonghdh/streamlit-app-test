import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import logging
import time

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

def get_new_id(df, column_name):
    """Generate a new ID for a given DataFrame column."""
    return 1 if df.empty else df[column_name].max() + 1

def save_to_csv(df, filepath, success_message):
    """Save a DataFrame to a CSV file and display a success message."""
    df.to_csv(filepath, index=False)
    st.success(success_message)

def main_define_metadata():
    """Show the editor for a specific TestID."""
    selected_test = st.session_state.get("selected_test")
    if not selected_test:
        st.write("No TestID selected.")
        return

    test_id = int(selected_test)

    st.title("Pre-Test")

    # Load CSV data
    df_test = read_csv_file(TESTS_CSV_FILE_PATH)
    df_user = read_csv_file(USERDATA_CSV_FILE_PATH)
    df_class = read_csv_file(CLASSDATA_CSV_FILE_PATH)
    df_attempt = read_csv_file(ATTEMPTDATA_CSV_FILE_PATH)

    # Filter for the selected TestID
    test_info = df_test[df_test['TestID'] == test_id]
    if test_info.empty:
        st.write(f"No data found for TestID {test_id} in TestsList.csv")
        return

    # Display test details
    st.write(f"### {test_id} - {test_info['TestName'].values[0]} (Language: {test_info['TestLanguage'].values[0]})")
    
    # User and Class selection
    cols = st.columns([1, 1])
    with cols[0]:
        selected_user_name = st.selectbox("Select User", options=df_user['UserName'])
        with st.expander("Create new User Name:"):
            new_user_input = st.text_input("Enter your User Name 👇", max_chars=20, label_visibility='collapsed').strip()
            if st.button("Add User Name"):
                if not new_user_input:
                    st.warning("Please input User Name!")
                elif new_user_input.lower() in df_user["UserName"].str.lower().values:
                    st.warning("The User Name already exists!")
                else:
                    new_user_df = pd.DataFrame({
                        'UserID': [get_new_id(df_user, 'UserID')],
                        'UserName': new_user_input,
                        'Password': ['123456']  # Default password for new users
                    })
                    df_user = pd.concat([df_user, new_user_df], ignore_index=True)
                    save_to_csv(df_user, USERDATA_CSV_FILE_PATH, "New User Name recorded successfully.")
                    time.sleep(0.8)
                    st.rerun()

    with cols[1]:
        selected_class_name = st.selectbox("Select Class", df_class['ClassName'])
        with st.expander("Create new Class Name:"):
            sub_cols = st.columns([1, 1])
            with sub_cols[0]:
                new_class_input = st.text_input("Enter your Class Name 👇", max_chars=20, label_visibility='collapsed').strip()
            with sub_cols[1]:
                new_teacher_input = st.text_input("Enter your Teacher Name 👇", max_chars=20, label_visibility='collapsed').strip()
            if st.button("Add New Class"):
                if not new_class_input:
                    st.warning("Please input Class Name!")
                elif new_class_input.lower() in df_class["ClassName"].str.lower().values:
                    st.warning("The Class Name already exists!")
                else:
                    new_class_df = pd.DataFrame({
                        'ClassID': [get_new_id(df_class, 'ClassID')],
                        'ClassName': new_class_input,
                        'TeacherName': new_teacher_input  #Temp can leave blank
                    })
                    df_class = pd.concat([df_class, new_class_df], ignore_index=True)
                    save_to_csv(df_class, CLASSDATA_CSV_FILE_PATH, "New Class Name recorded successfully.")
                    time.sleep(0.8)
                    st.rerun()
    # Action buttons
    button_cols = st.columns([1, 2, 1])
    with button_cols[0]:
        if st.button("🔙 Back"):
            st.session_state.page = 'test_list'
            st.session_state.selected_test = None
            st.rerun()
    with button_cols[1]:
        st.write(" ")
    with button_cols[2]:
        if st.button("Do Test"):
            selected_user_id = df_user.loc[df_user['UserName'] == selected_user_name, 'UserID'].values[0]
            selected_class_id = df_class.loc[df_class['ClassName'] == selected_class_name, 'ClassID'].values[0]
            new_attempt_id = get_new_id(df_attempt, 'AttemptID')
        
            new_attempt_df = pd.DataFrame({
                'AttemptID': [new_attempt_id],
                'UserID': [selected_user_id],
                'ClassID': [selected_class_id],
                'TestID': [test_id],
                'TotalQuestion': [''],
                'CorrectList': [''],
                'WrongList': ['']
            })

            df_attempt = pd.concat([df_attempt, new_attempt_df], ignore_index=True)
            save_to_csv(df_attempt, ATTEMPTDATA_CSV_FILE_PATH, "Test attempt recorded successfully.")
            #time.sleep(0.8)
            #st.rerun()

# Run the main function
main_define_metadata()

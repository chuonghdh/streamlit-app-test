import streamlit as st
import pandas as pd
import os

def set_custom_css():
    """Set custom CSS for wider table, row borders, and hover effects."""
    st.markdown(
        """
        <style>
        .streamlit-expanderHeader {
            font-size: 0.2rem;
        }
        .block-container {
            max-width: 900px;
            padding: 0.2rem 0.2rem;
        }
        .stButton>button {
            width: 100%;
        }
        .table-header {
            display: flex;
            background-color: #f0f0f0;
            padding: 2px;
            font-weight: bold;
            border-bottom: 1px solid #ccc;
            margin-bottom: 2px;
        }
        .table-row {
            display: flex;
            padding: 0.2px;
            border: 1px solid lightgray;
            margin-bottom: 1px;
            transition: background-color 0.3s ease;
        }
        .table-row:hover {
            background-color: #f0f0f0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Constants for file paths
TESTS_CSV_FILE_PATH = 'Data/TestsList.csv'
WORDS_CSV_FILE_PATH = 'Data/WordsList.csv'
USERDATA_CSV_FILE_PATH = 'Data/UserData.csv'
CLASSDATA_CSV_FILE_PATH = 'Data/ClassData.csv'
ATTEMPTDATA_CSV_FILE_PATH = 'Data/AttemptData.csv'

# File path for the CSV in the Streamlit environment
prd_TestsList_path = 'prd_Data/prd_TestsListData.csv'
prd_WordsList_path = 'prd_Data/prd_WordsListData.csv'
prd_UserData_path = 'prd_Data/prd_UserData.csv'
prd_ClassData_path = 'prd_Data/prd_ClassData.csv'
prd_AttemptData_path = 'prd_Data/prd_AttemptData.csv'

def read_csv_file(repo_path, prd_path):
    """Read data from a CSV file."""
    try:
        if os.path.exists(prd_path):
            df = pd.read_csv(prd_path)
            #st.info("Data loaded from local storage.")
        else:
            # Initial load from a repository, as a fallback (if needed)
            df = pd.read_csv(repo_path)  # Replace with your default CSV
            df.to_csv(prd_path, index=False)  # Save to local environment
            #st.info("Data loaded from repository and saved to local storage.")
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError) as e:
        st.error(f"Error loading file: {repo_path} - {str(e)}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return pd.DataFrame()

def initialize_folder(folder):
    # Directory path
    directory_path = folder

    # Create the directory if it doesn't exist
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def initialize_data():
    # Load CSV data
    df_test = read_csv_file(TESTS_CSV_FILE_PATH, prd_TestsList_path)
    df_word = read_csv_file(WORDS_CSV_FILE_PATH, prd_WordsList_path)
    df_user = read_csv_file(USERDATA_CSV_FILE_PATH, prd_UserData_path)
    df_class = read_csv_file(CLASSDATA_CSV_FILE_PATH, prd_ClassData_path)
    df_attempt = read_csv_file(ATTEMPTDATA_CSV_FILE_PATH, prd_AttemptData_path)

    # Clear variables to free up memory
    del df_test, df_word, df_user, df_class, df_attempt

def main():

    initialize_folder('prd_Data')
    initialize_data()
    set_custom_css()
    
    # Define pages with their titles and file paths
    pages = {
        "Do Your Test": [
            ("List of all tests", "Do_Test/all_tests_list.py"),
        ],
        "Manage Your Test": [
            ("Edit current test", "Manage_Test/edit_test.py"),
            ("Backup tests data", "Manage_Test/backup_tests.py"),
        ]
    }

    # Sidebar navigation
    st.sidebar.title("Navigation")
    if st.sidebar.button('List of all tests'):
        st.session_state.page = 'test_list'
        st.session_state.url = 'Do_Test/all_tests_list.py'
        st.rerun()  # Reload the page to reflect the new selection
    if st.sidebar.button('Edit current test'):
        st.session_state.page = 'table'
        st.session_state.url = 'Manage_Test/edit_test.py'
        st.rerun()  # Reload the page to reflect the new selection
    if st.sidebar.button('Backup tests data'):
        st.session_state.page = 'backup'
        st.session_state.url = 'Manage_Test/backup_tests.py'
        st.rerun()  # Reload the page to reflect the new selection

    # Display the selected page
    if "page" in st.session_state:
        st.write(f"Selected Page: {st.session_state.page}") #IMPORTANT FOR DEBUG
        # Open the file with the correct encoding (usually UTF-8)
        with open(st.session_state.url, 'r', encoding='utf-8') as f:
            code = f.read()
        exec(code, globals())  # Execute the selected page
    else:
        st.session_state.page = 'test_list'
        st.session_state.url = 'Do_Test/all_tests_list.py'
        st.rerun()

if __name__ == "__main__":
    main()

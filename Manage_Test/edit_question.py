import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Constants
TESTS_CSV_FILE_PATH = 'data/TestsList.csv'  # Adjust the path if necessary
WORDS_CSV_FILE_PATH = 'data/WordsList.csv'  # Adjust the path if necessary

def read_csv_file(filename):
    """Read data from a CSV file."""
    try:
        return pd.read_csv(filename)
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return pd.DataFrame()

def get_filtered_words(test_id):
    """Read and filter the WordsList.csv file based on the TestID."""
    try:
        df_words = read_csv_file(WORDS_CSV_FILE_PATH)
        filtered_words = df_words[df_words['TestID'] == int(test_id)]
        return filtered_words, df_words  # Return both the filtered and full DataFrame
    except Exception as e:
        st.error(f"Error filtering WordsList.csv: {e}")
        return pd.DataFrame(), pd.DataFrame()

def show_editable_table_with_delete(df, full_df, test_id):
    """Display the editable table with AgGrid, including delete functionality, and return the edited DataFrame."""
    gb = GridOptionsBuilder.from_dataframe(df)
    
    # Enable cell editing
    gb.configure_default_column(editable=True)
    
    # Configure pagination and selection
    gb.configure_selection('single', use_checkbox=True)
    
    # Build grid options
    grid_options = gb.build()

    # Display the grid
    grid_return = AgGrid(
        df, 
        gridOptions=grid_options, 
        update_mode=GridUpdateMode.MODEL_CHANGED | GridUpdateMode.SELECTION_CHANGED
    )
    
    # Extract selected rows
    selected_rows = grid_return.get('selected_rows', [])
    st.write("Selected Rows:", selected_rows)  # Debugging output

    # Make the button always visible
    delete_button_visible = False

    # Check if selected_rows is non-empty and contains valid data
    if isinstance(selected_rows, list) and len(selected_rows) > 0:
        # Ensure the first element of selected_rows is a dictionary and contains 'WordID'
        if isinstance(selected_rows[0], dict) and 'WordID' in selected_rows[0]:
            delete_button_visible = True  # Indicate that the delete button should be visible

            word_id_to_delete = selected_rows[0]['WordID']
            
            # Display the delete button
            if st.button("Delete Selected Word"):
                try:
                    # Filter out the row with the selected WordID
                    full_df = full_df[full_df['WordID'] != word_id_to_delete]
                    
                    # Save the updated DataFrame back to the CSV
                    full_df.to_csv(WORDS_CSV_FILE_PATH, index=False)
                    
                    st.success(f"Word ID {word_id_to_delete} has been deleted successfully!")
                    st.experimental_rerun()  # Refresh the page to reflect the changes
                except Exception as e:
                    st.error(f"Error deleting word: {e}")
        else:
            st.error("No 'WordID' found in the selected row or selected row is not valid.")
    
    # Display the delete button even if no row is selected (for testing visibility)
    if not delete_button_visible:
        st.warning("Please select a row to enable deletion.")
    
    # Get the edited DataFrame after changes
    edited_df = grid_return['data']
    return edited_df

def update_words_csv(updated_df, full_df, test_id):
    """Update the WordsList.csv file with the edited DataFrame for the specific TestID."""
    try:
        # Drop the rows with the current TestID from the original DataFrame
        full_df = full_df[full_df['TestID'] != int(test_id)]
        
        # Append the updated rows for the current TestID
        full_df = pd.concat([full_df, updated_df], ignore_index=True)
        
        # Debugging: Display unique Test IDs to ensure data integrity
        st.write(f'Unique Test IDs = {full_df["TestID"].unique()}')

        # Save the updated DataFrame back to the CSV
        full_df.to_csv(WORDS_CSV_FILE_PATH, index=False)
        st.success("WordsList.csv has been updated successfully!")
    except Exception as e:
        st.error(f"Error updating WordsList.csv: {e}")

def insert_new_word(new_word, new_LanguageCode, new_WordPhonetic, new_WordDescription, new_WordImageLink, full_df, test_id):
    """Insert a new word into the WordsList.csv file."""
    if not new_word or not new_LanguageCode or not new_WordPhonetic or not new_WordDescription:
        st.error("All fields except Image Link must be filled out.")
        return
    
    try:
        # Auto-generate the WordID as max WordID + 1
        new_word_id = full_df['WordID'].max() + 1

        # Create a new row for the new word
        new_row = {
            'WordID': new_word_id,
            'TestID': int(test_id),
            'Word': new_word,
            'LanguageCode': new_LanguageCode,
            'WordPhonetic': new_WordPhonetic,
            'Description': new_WordDescription,
            'Image': new_WordImageLink,
        }

        # Convert the new row to a DataFrame
        new_row_df = pd.DataFrame([new_row])

        # Concatenate the new row with the full DataFrame
        full_df = pd.concat([full_df, new_row_df], ignore_index=True)

        # Save the updated DataFrame back to the CSV
        full_df.to_csv(WORDS_CSV_FILE_PATH, index=False)
        st.success("New word has been added successfully!")
        st.rerun()
    except Exception as e:
        st.error(f"Error inserting new word: {e}")

def show_question_editor():
    """Show the editor for a specific TestID."""
    selected_test = st.session_state.get("selected_test")

    if not selected_test:
        st.write("No TestID selected.")
        return

    test_id = selected_test
    df_tests = read_csv_file(TESTS_CSV_FILE_PATH)

    # Filter the DataFrame for the selected TestID in TestsList.csv
    if df_tests[df_tests['TestID'] == int(test_id)].empty:
        st.write(f"No data found for TestID {test_id} in TestsList.csv")
        return

    st.write(f"### Edit Words for Test ID: {test_id}")

    # Get the filtered words data and the full DataFrame from WordsList.csv
    df_words, full_df = get_filtered_words(test_id)

    if df_words.empty:
        st.error(f"No words data found for TestID {test_id} in WordsList.csv")
        if st.button("🔙 Back to Main Page"):
            st.session_state.page = 'table'
            st.rerun()
        return

    # Display the insert form
    st.write("#### Add a New Word")
    new_word = st.text_input("New word")
    new_LanguageCode = st.text_input("Language Code")
    new_WordPhonetic = st.text_input("Phonetic or Examples")
    new_WordDescription = st.text_input("Word Description")
    new_WordImageLink = st.text_input("Image Link")
    
    if st.button("Add Word"):
        insert_new_word(new_word, new_LanguageCode, new_WordPhonetic, new_WordDescription, new_WordImageLink, full_df, test_id)

    # Display the editable table with delete functionality
    edited_df = show_editable_table_with_delete(df_words, full_df, test_id)

    # Update the CSV file when the button is clicked
    if st.button("Update"):
        update_words_csv(edited_df, full_df, test_id)

    # Add a back button to return to the main page
    if st.button("🔙 Back to Main Page"):
        st.session_state.page = 'table'
        st.rerun()

# Ensure 'page' is initialized
if "page" not in st.session_state:
    st.session_state["page"] = "table"  # Default to the main table
elif st.session_state.page == 'edit_question':
    show_question_editor()

import os
import requests
import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import ImageOps, Image

from Manage_Test.edit_question import show_question_editor

# Constants
CSV_FILE_PATH = 'data\TestsList.csv'
PLACEHOLDER_IMAGE = "data\image\placeholder_image.png"
IMAGE_SIZE = 60

# Utility Functions
def cache_clear():
    """Clear Streamlit cache."""
    st.cache_data.clear()

# CSV-related Functions
@st.cache_data
def read_csv_file(filename=CSV_FILE_PATH):
    """Read data from the CSV file."""
    try:
        if os.path.exists(filename):
            return pd.read_csv(filename)
        else:
            return pd.DataFrame()  # Return an empty DataFrame if the file doesn't exist
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return pd.DataFrame()

def save_to_csv(data, filename=CSV_FILE_PATH):
    """Save data to the CSV file."""
    try:
        new_df = pd.DataFrame(data)
        if os.path.exists(filename):
            df = read_csv_file(filename)
            df = pd.concat([df, new_df], ignore_index=True)
        else:
            df = new_df
        df.to_csv(filename, index=False)
        cache_clear()
        st.success("Data saved successfully.")
    except Exception as e:
        st.error(f"Error saving data to CSV: {e}")

def delete_from_csv(row_index, filename=CSV_FILE_PATH):
    """Delete a row from the CSV file."""
    try:
        if os.path.exists(filename):
            df = read_csv_file(filename)
            df = df.drop(index=row_index)
            df.to_csv(filename, index=False)
            cache_clear()
            st.success("Row deleted successfully.")
    except Exception as e:
        st.error(f"Error deleting row from CSV: {e}")

def update_csv_file(row_index, new_data, filename=CSV_FILE_PATH):
    """Update a row in the CSV file."""
    try:
        if os.path.exists(filename):
            df = read_csv_file(filename)
            df.loc[row_index] = new_data
            df.to_csv(filename, index=False)
            cache_clear()
            st.success("Data updated successfully.")
    except Exception as e:
        st.error(f"Error updating CSV file: {e}")

# Image-related Functions
@st.cache_data
def fetch_image(link):
    """Fetch image from the provided URL."""
    try:
        if not pd.isna(link) and link.strip():
            response = requests.get(link)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
    except Exception:
        pass  # Silent fail on error
    return None

def resize_and_crop_image(image, size):
    """Resize and crop the image to a square."""
    try:
        return ImageOps.fit(image, (size, size), Image.LANCZOS)
    except Exception:
        return None

def display_image_or_text(link, column, size=IMAGE_SIZE):
    """Display image or placeholder if the link is invalid."""
    image = fetch_image(link)
    
    if image:
        image = resize_and_crop_image(image, size)
        if image:
            column.image(image, width=size)
    if not image:  # If fetching image failed, show the placeholder
        try:
            placeholder = Image.open(PLACEHOLDER_IMAGE)
            placeholder = resize_and_crop_image(placeholder, size)
            if placeholder:
                column.image(placeholder, width=size)
        except Exception as e:
            st.error(f"Error displaying placeholder image: {e}")

# UI Functions
def show_data_table():
    """Display the data table with rename, delete, and edit question options."""
    df = read_csv_file()
    if df.empty:
        st.write("No tests available.")
        return

    st.write("### Edit Your Tests")  # Main Page Title

    # Set custom CSS for headers, row borders, and hover effects
    set_custom_css()

    # Display the table header
    st.write(
        """
        <div class='table-header'>
            <span style="flex: 0.3;">ID</span>
            <span style="flex: 1;">Name</span>
            <span style="flex: 1;">Description</span>
            <span style="flex: 0.3;">Lang</span>
            <span style="flex: 0.5;">Image</span>
            <span style="flex: 0.5;">Created By</span>
            <span style="flex: 0.5;">Updated By</span>
            <span style="flex: 0.45;"></span>
            <span style="flex: 0.45;"></span>
            <span style="flex: 0.6;"></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if 'rename_mode' not in st.session_state:
        st.session_state.rename_mode = None  # Track the index of the row in rename mode

    for i, row in df.iterrows():
        display_table_row(i, row, df)

    if st.button('➕ Add Test'):
        st.session_state.page = 'form'
        st.rerun()

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

def display_table_row(row_index, row, df):
    """Display a single row in the data table."""
    num_columns = len(row) + 3  # Additional column for the 'Edit Questions' button
    cols = st.columns([0.3, 1, 1, 0.2, 0.5, 0.5, 0.5, 0.45, 0.45, 0.6][:num_columns])

    # Wrap the row in a div with the class 'table-row' for styling
    with st.container():
        st.write('<div class="table-row">', unsafe_allow_html=True)
        
        if st.session_state.rename_mode == row_index:
            handle_rename_mode(row_index, row, cols)
        else:
            handle_normal_mode(row_index, row, cols)

        st.write('</div>', unsafe_allow_html=True)

def handle_rename_mode(row_index, row, cols):
    """Handle the rename mode for a row, allowing only certain fields to be edited."""
    new_data = []
    for j, (col_name, col_value) in enumerate(row.items()):
        if col_name in ['TestName', 'TestDescription', 'Image']:
            new_data.append(cols[j].text_input(f' ', value=col_value, key=f'{col_name}_{row_index}'))
        else:
            new_data.append(col_value)
            cols[j].write(col_value)

    done_button = cols[len(row)].button('✅ Done', key=f'done_{row_index}')
    if done_button:
        st.session_state.rename_mode = None
        update_csv_file(row_index, new_data)
        st.rerun()

def handle_normal_mode(row_index, row, cols):
    """Handle the normal mode for a row."""
    for j, (col_name, col_value) in enumerate(row.items()):
        if col_name == 'Image':
            display_image_or_text(col_value, cols[j])
        else:
            if col_name == 'TestID':
                col_value_int = int(col_value)  # Convert col_value to an integer and then display it
                cols[j].markdown(f"<p style='font-size:16px; font-weight:bold;'>{col_value_int}</p>", unsafe_allow_html=True)
            elif col_name in ['TestDescription', 'Language', 'CreatedBy', 'LastUpdatedBy']:
                cols[j].markdown(f"<p style='font-size:12px;'>{col_value}</p>", unsafe_allow_html=True)
            elif col_name == 'TestName':
                cols[j].markdown(f"<p style='font-size:16px; font-weight:bold;'>{col_value}</p>", unsafe_allow_html=True)
            else:
                cols[j].write(col_value)

    edit_questions_button = cols[len(row)].button(
        label="📝", 
        help="Edit Questions",
        key=f'edit_questions_{row_index}'
    )
    rename_button = cols[len(row) + 1].button(
        label="✏️", 
        help="Rename",
        key=f'rename_{row_index}'
    )
    delete_button = cols[len(row) + 2].button(
        label="🗑️", 
        help="Delete",
        key=f'delete_{row_index}'
    )
    
    if edit_questions_button:
        st.session_state.selected_test = row['TestID']
        st.session_state.page = 'edit_question'
        st.rerun()

    if rename_button:
        st.session_state.rename_mode = row_index
        st.rerun()

    if delete_button:
        delete_from_csv(row_index)
        st.rerun() 

def add_test_form():
    """Create and handle the add test form."""
    st.write("### Add New Entry")
    form = st.form(key='add_entry_form')

    df = read_csv_file()

    if df.empty:
        new_test_id = 1  # Start TestID from 1 if the dataframe is empty
    else:
        df['TestID'] = pd.to_numeric(df['TestID'], errors='coerce')
        new_test_id = df['TestID'].max() + 1

    form.text_input('TestID', value=str(new_test_id), disabled=True, key='TestID')

    form_data = {col: form.text_input(f'Enter the {col}:') for col in df.columns if col != 'TestID'}

    submit, cancel = form.columns(2)
    if submit.form_submit_button(label='Add Entry'):
        form_data['TestID'] = str(new_test_id)
        new_entry = {col: [form_data[col]] for col in df.columns}
        save_to_csv(new_entry)
        st.session_state.page = 'table'
        st.rerun()

    if cancel.form_submit_button(label='Cancel'):
        st.session_state.page = 'table'
        st.rerun()

def edit_questions_page():
    """Display the edit questions page for the selected test."""
    test_id = st.session_state.selected_test
    st.write(f"### Edit Questions for Test ID: {test_id}")

    if st.button("🔙 Back to Main Page"):
        st.session_state.page = 'table'
        st.rerun()

def show_page_testlist():
    """Page routing logic."""
    if st.session_state.page == 'table':
        show_data_table()
    elif st.session_state.page == 'form':
        add_test_form()
    elif st.session_state.page == 'edit_question':
        #edit_questions_page()
        show_question_editor()

# Main Page of Edit Test

if 'page' not in st.session_state:
    st.session_state.page = 'table'
if 'selected_test' not in st.session_state:
    st.session_state.selected_test = None

show_page_testlist()

#if __name__ == '__main__':
#    main()

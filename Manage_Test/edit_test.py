import streamlit as st
import pandas as pd

# Path to your CSV file
csv_file_path = 'Data/TestsList.csv'

# Read the CSV file into a DataFrame
if 'df' not in st.session_state:
    st.session_state.df = pd.read_csv(csv_file_path)

df = st.session_state.df

# Streamlit app
st.title('Read and Edit CSV File')

# Check if we're in edit mode
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'selected_index' not in st.session_state:
    st.session_state.selected_index = None
if 'trigger_rerun' not in st.session_state:
    st.session_state.trigger_rerun = False

def show_table():
    """Display the table with an edit button for each row."""
    st.write("Here is the content of the CSV file:")
    for i, row in df.iterrows():
        cols = st.columns(len(df.columns) + 1)
        for j, col in enumerate(df.columns):
            if col.lower() == 'image':  # Check if the column name is 'image'
                try:
                    cols[j].image(row[col], width=100)  # Display the image
                except:
                    cols[j].write("Invalid image link")
            else:
                cols[j].write(row[col])
        if cols[len(df.columns)].button("Edit", key=f"edit_button_{i}", on_click=enter_edit_mode, args=(i,)):
            pass

def show_edit_form():
    """Display the form to edit the selected row."""
    selected_index = st.session_state.selected_index
    st.write(f"Edit the details for: {df.at[selected_index, 'TestName']}")
    columns = df.columns.tolist()

    form_data = {}
    with st.form(key='edit_form'):
        for col in columns:
            form_data[col] = st.text_input(label=col, value=str(df.at[selected_index, col]))  # Convert value to string

        if st.form_submit_button(label='Submit'):
            submit_update(form_data)

def submit_update(form_data):
    """Update the DataFrame with the form data and save it to the CSV file."""
    selected_index = st.session_state.selected_index
    for col, value in form_data.items():
        # Convert form data to the appropriate dtype
        if pd.api.types.is_numeric_dtype(df[col]):
            df.at[selected_index, col] = pd.to_numeric(value, errors='coerce')
        else:
            df.at[selected_index, col] = value
    # Save the updated DataFrame to a CSV file
    df.to_csv(csv_file_path, index=False)
    st.success(f'Details for {df.at[selected_index, "TestName"]} have been updated.')
    exit_edit_mode()  # Exit edit mode
    st.session_state.trigger_rerun = True

def enter_edit_mode(index):
    """Enter edit mode and set the selected index."""
    st.session_state.edit_mode = True
    st.session_state.selected_index = index
    st.session_state.trigger_rerun = True

def exit_edit_mode():
    """Exit edit mode and clear the selected index."""
    st.session_state.edit_mode = False
    st.session_state.selected_index = None
    st.session_state.trigger_rerun = True

# Check if a rerun is needed
if st.session_state.trigger_rerun:
    st.session_state.trigger_rerun = False
    st.experimental_set_query_params()  # Trigger a rerun using a no-op query param update

# Display the table or the form based on the mode
if st.session_state.edit_mode:
    show_edit_form()
    if st.button("Back to Main Page"):
        exit_edit_mode()
        st.session_state.trigger_rerun = True
else:
    show_table()

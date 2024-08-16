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

# Display the table or the form based on the mode
if not st.session_state.edit_mode:
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
        if cols[len(df.columns)].button("Edit", key=f"edit_button_{i}"):
            st.session_state.edit_mode = True
            st.session_state.selected_index = i
else:
    selected_index = st.session_state.selected_index
    st.write(f"Edit the details for: {df.at[selected_index, 'TestName']}")
    columns = df.columns.tolist()
    form_data = {}

    with st.form(key='edit_form'):
        for col in columns:
            form_data[col] = st.text_input(label=col, value=str(df.at[selected_index, col]))  # Convert value to string

        if st.form_submit_button(label='Save'):
            for col in columns:
                df.at[selected_index, col] = form_data[col]
            st.session_state.df = df  # Update the session state
            df.to_csv(csv_file_path, index=False)  # Save the updated DataFrame to a CSV file
            st.success(f'Details for {df.at[selected_index, "TestName"]} have been updated.')
            st.session_state.edit_mode = False  # Exit edit mode

    # Add a button to go back to the main page
    if st.button("Back to Main Page"):
        st.session_state.edit_mode = False  # Exit edit mode

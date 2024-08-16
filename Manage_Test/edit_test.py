import streamlit as st
import pandas as pd

# Path to your CSV file
csv_file_path = 'data/TestsList.csv'

# Read the CSV file into a DataFrame
if 'df' not in st.session_state:
    st.session_state.df = pd.read_csv(csv_file_path)

df = st.session_state.df

# Streamlit app
st.title('Read and Edit CSV File')

# Check for query parameters to determine if we're in the edit mode
query_params = st.query_params
selected_index = query_params.get('edit')

# If no selected index, display the main table
if selected_index is None:
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
            # Set the query parameter and update the URL to edit mode
            st.set_query_params(edit=i)

else:
    # Display the edit form for the selected row
    selected_index = int(selected_index[0])  # Convert the selected index to integer
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
            # Clear the query params to return to the main page
            st.set_query_params()

    # Add a button to go back to the main page
    if st.button("Back to Main Page"):
        st.set_query_params()  # Clear the query params to return to the main page

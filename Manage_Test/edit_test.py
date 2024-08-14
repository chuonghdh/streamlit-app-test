
import pandas as pd
import gdown
import streamlit as st
import openpyxl


def read_test_list(name):
    st.title('Edit Tests')
    st.write('This is a page to Edit Current Tests')
    st.write('hahaha')

# Calling the function
# read_test_list("Alice")   

# Function to download file from Google Drive
def download_file_from_google_drive(file_id, output_path):
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output_path, quiet=False)

# Function to upload file to Google Drive
def upload_file_to_google_drive(file_path, file_name):
    # Import Google Drive API related packages
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    # Google Drive API credentials
    SERVICE_ACCOUNT_FILE = 'credentials.json'  # Update with your credentials file path
    SCOPES = ['https://www.googleapis.com/auth/drive']

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('drive', 'v3', credentials=credentials)

    # Search for existing file in Google Drive
    query = f"name='{file_name}' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])

    if items:
        # Update existing file
        file_id = items[0]['id']
        media = MediaFileUpload(file_path, resumable=True)
        updated_file = service.files().update(fileId=file_id, media_body=media).execute()
        return updated_file.get('id')
    else:
        # Upload new file
        file_metadata = {'name': file_name}
        media = MediaFileUpload(file_path, resumable=True)
        uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return uploaded_file.get('id')

# Google Drive file ID and output path
# https://docs.google.com/spreadsheets/d/17YxueOUwow5vJBgKxALlyNtxs9qtmQaj/edit?usp=sharing&ouid=117920818199174565935&rtpof=true&sd=true
# https://docs.google.com/spreadsheets/d/1a1OPldUzDnQuCrllN6ebc35tfAXv44FE/edit?usp=sharing&ouid=117186288122919854960&rtpof=true&sd=true
file_id = '17YxueOUwow5vJBgKxALlyNtxs9qtmQaj' #'1eZnbPTimvWoIFbeRnQ2KPziY0P-g_MvO' # 'YOUR_FILE_ID'
output_path = 'TestsList.xlsx'
file_name = 'TestsList.xlsx'

# Download the file
download_file_from_google_drive(file_id, output_path)

# Read the Excel file into a DataFrame
df = pd.read_excel(output_path)

# Display the DataFrame in Streamlit
st.write("Here is the data from the Excel file:")
st.dataframe(df)

# Form for user input
st.write("Add a new row to the table:")
with st.form(key='new_row_form'):
    columns = df.columns
    new_row_data = {}
    for col in columns:
        new_row_data[col] = st.text_input(f"Enter {col}")

    submit_button = st.form_submit_button(label='Add Row')

# Append new data to DataFrame and save
if submit_button:
    new_row = pd.DataFrame(new_row_data, index=[0])
    st.write("New row:", new_row)

    df = pd.concat([df, new_row], ignore_index=True)
    st.write("Append successful")
    
    # Create a DataFrame for the new row
    #new_row_df = pd.DataFrame([new_row])
    #st.write("New row DataFrame:", new_row_df)

    # Concatenate the new row DataFrame with the existing DataFrame
    #df = pd.concat([df, new_row_df], ignore_index=True)
    df.to_excel(output_path, index=False, engine='openpyxl')
    

    # Upload the updated file back to Google Drive
    upload_file_to_google_drive(output_path, file_name)
    st.success("New row added and file uploaded to Google Drive successfully!")

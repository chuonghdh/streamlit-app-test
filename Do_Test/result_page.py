import streamlit as st
import pandas as pd
import requests

def main_result_page():
    # Handle paging displaying session
    if st.session_state.page == 'result_page':
        result_df = st.session_state.get('test_result')
        st.data_editor(result_df, disabled=True)
    else: 
        st.session_state.page == 'test_list'
        return
    
    if st.button("🔙 Back", key='result_page_back'):
        st.session_state.page = 'test_list'
        st.session_state.selected_test = None
        st.session_state.test_result = None
        st.session_state.AttemptID = None
        st.rerun()
    
main_result_page()
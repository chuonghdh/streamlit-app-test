import streamlit as st
import pandas as pd
import requests
from streamlit_js_eval import streamlit_js_eval

def update_test_result_df(df, word_index, score):
    df.loc[df['order'] == word_index, ['Score', 'Complete']] = [score, 'Y']
    return df

def main_result_page():
    # Handle paging displaying session
    if st.session_state.page == 'result_page':
        score = streamlit_js_eval(js_expressions="sessionStorage.getItem('wordScore')", key="WORD_SCORE3")
        st.session_state.test_result = update_test_result_df(st.session_state.test_result, st.session_state.word_index, score)
        result_df = st.session_state.get('test_result')
        st.data_editor(result_df, disabled=True)
    else: 
        st.session_state.page == 'test_list'
        return
    streamlit_js_eval(js_expressions="sessionStorage.setItem('wordScore', '0');")
    if st.button("🔙 Back", key='result_page_back'):
        st.session_state.page = 'test_list'
        st.session_state.word_index = 1
        st.session_state.selected_test = None
        st.session_state.test_result = None
        st.session_state.AttemptID = None
        st.rerun()
    
main_result_page()
import streamlit as st
import pandas as pd
import requests
from streamlit_js_eval import streamlit_js_eval

def update_test_result_df(df, word_index, score):
    df.loc[df['order'] == word_index, ['Score', 'Complete']] = [score, 'Y']
    return df

def main_result_page():
    temp = streamlit_js_eval(js_expressions="sessionStorage.getItem('wordScore');", key = "Get_Score4")
    
    if temp != -1 and temp is not None: 
        st.session_state.last_score = float(temp)
        st.session_state.test_result = update_test_result_df(st.session_state.test_result, st.session_state.word_index, st.session_state.last_score)
    
    #streamlit_js_eval(js_expressions="sessionStorage.clear();", key="clear1")
    streamlit_js_eval(js_expressions="sessionStorage.setItem('wordScore', -1);", key="clear2")
    # Handle paging displaying session
    if st.session_state.page == 'result_page':
        # Show final result
        result_df = st.session_state.get('test_result')
        st.data_editor(result_df, disabled=True)
    else: 
        st.session_state.page == 'test_list'
        return
    
    # Clear the session storage using JavaScript
    #streamlit_js_eval("sessionStorage.clear();", key="clear")
    #streamlit_js_eval(js_expressions="sessionStorage.setItem('wordScore', -1);", key="Set_Score")
    if st.button("🔙 Back", key='result_page_back'):
        st.session_state.page = 'test_list'
        st.session_state.word_index = 1
        st.session_state.selected_test = None
        st.session_state.test_result = None
        st.session_state.AttemptID = None
        st.rerun()
    
main_result_page()
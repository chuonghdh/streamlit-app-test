'''
st.title('Hello, Streamlit!')
st.write('This is a simple web app with Streamlit.')

number = st.slider('Pick a number', 0, 100)
st.write('You picked:', number)
'''

import streamlit as st

def main():

    pages = {
        "Do Your Test": [
            st.Page("Do_Test/all_tests_list.py", title="List of all tests"),
            st.Page("Do_Test/your_last_tests.py", title="Your last taken tests"),
        ],
        "Manage Your Test": [
            st.Page("Manage_Test/edit_test.py", title="Edit current test"), 
        ]
    }

    pg = st.navigation(pages)
    pg.run()

if __name__ == "__main__":
    main()
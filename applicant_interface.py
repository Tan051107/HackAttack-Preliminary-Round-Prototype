import streamlit as st
from applicant_dashboard import applicant_dashboard
from applicant_view_saved_job import view_saved_jobs
from applicant_application_status import application_status

def home():
    applicant_dashboard()

def page_one():
    application_status()

def page_two():
    view_saved_jobs()

def main():
    if 'page' not in st.session_state:
        st.session_state.page = 'Home'

    st.sidebar.title("Menu")
    # Using buttons to select pages
    if st.sidebar.button("Home"):
        st.session_state.page = 'Home'
    if st.sidebar.button("View Application Status"):
        st.session_state.page = 'Page One'
    if st.sidebar.button("Saved Jobs"):
        st.session_state.page = 'Page Two'

    # Show the selected page
    if st.session_state.page == 'Home':
        home()
    elif st.session_state.page == 'Page One':
        page_one()
    elif st.session_state.page == 'Page Two':
        page_two()


if __name__ == "__main__":
    main()
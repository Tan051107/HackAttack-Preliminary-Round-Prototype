import streamlit as st
from recruiter_dashboard import show_parsed_resumes
from view_saved_applicant import show_saved_applicants
from view_interview_applicant import show_invited_applicants
from view_sent_offer_applicant import show_offered_applicants
from job_listings import job_board
from candidate_comparison import candidate_comparison
from view_suspicious_resume import view_suspicious_resume

def home():
    show_parsed_resumes()

def page_one():
    show_invited_applicants()

def page_two():
    show_offered_applicants()

def page_three():
    view_suspicious_resume()


def page_four():
    candidate_comparison()

def page_five():
    show_saved_applicants()

def page_six():
    job_board()

def main():
    if 'page' not in st.session_state:
        st.session_state.page = 'Home'

    st.sidebar.title("Menu")
    # Using buttons to select pages
    if st.sidebar.button("Home"):
        st.session_state.page = 'Home'
    if st.sidebar.button("To Be Interviewed"):
        st.session_state.page = 'Page One'
    if st.sidebar.button("Offered"):
        st.session_state.page = 'Page Two'
    if st.sidebar.button("Suspicious Applicants"):
        st.session_state.page = 'Page Three'
    if st.sidebar.button("Candidate Comparison"):
        st.session_state.page = 'Page Four'
    if st.sidebar.button("View Saved Candidates"):
        st.session_state.page = 'Page Five'
    if st.sidebar.button("Job Listings"):
        st.session_state.page = 'Page Six'

    # Show the selected page
    if st.session_state.page == 'Home':
        home()
    elif st.session_state.page == 'Page One':
        page_one()
    elif st.session_state.page == 'Page Two':
        page_two()
    elif st.session_state.page == 'Page Three':
        page_three()
    elif st.session_state.page == 'Page Four':
        page_four()
    elif st.session_state.page == 'Page Five':
        page_five()
    else:
        page_six()

if __name__ == "__main__":
    main()

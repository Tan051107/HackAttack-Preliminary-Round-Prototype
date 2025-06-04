import streamlit as st
import pandas as pd

# Load CSV once at the top
@st.cache_data
def load_data():
    df = pd.read_csv("parsed_data/results.csv")
    df['name'] = df['name'].str.strip()  # Clean whitespace
    return df

# Define function to display applications
def application_status():
    df = load_data()
    applicant_rows = df[df['name'] == "Tan Yik Yang"]

    st.title("Application Status")

    if not applicant_rows.empty:
        for idx, row in applicant_rows.iterrows():
            data = {
                "Name": row["name"],
                "Status": row["status"],
                "Job Title Applied": row["job_title"],
                "Company Applied To": row["company"]
            }

            if str(row["status"]).strip().lower() == "interview invited":
                data["Interview Date"] = row.get("interview_date", "N/A")
                data["Interview Time"] = row.get("interview_time", "N/A")

            display_df = pd.DataFrame(data.items(), columns=["Field", "Value"])
            st.subheader(f"Application #{idx + 1}")
            st.table(display_df)
    else:
        st.warning("No applications found.")

application_status()


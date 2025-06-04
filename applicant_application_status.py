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

    st.title("Application Status")

    # Get unique names for selection
    names = df['name'].dropna().unique()
    if len(names) == 0:
        st.warning("No applicant names found.")
        return

    selected_name = st.selectbox("Select your name", sorted(names))

    # Filter rows for selected applicant
    applicant_rows = df[df['name'] == selected_name]

    if not applicant_rows.empty:
        for idx, row in applicant_rows.iterrows():
            data = {
                "Name": row["name"],
                "Status": row["status"],
                "Job Title Applied": row["job_title"],
                "Company Applied To": row["company"]
            }

            # Include interview info if applicable
            if str(row["status"]).strip().lower() == "interview invited":
                data["Interview Date"] = row.get("interview_date") or "Not Scheduled"
                data["Interview Time"] = row.get("interview_time") or "Not Scheduled"

            display_df = pd.DataFrame(data.items(), columns=["Field", "Value"])

            # Use expander for clean layout
            with st.expander(f"{row['job_title']} at {row['company']}"):
                st.table(display_df)
    else:
        st.warning("No applications found for this applicant.")

# Run the function
application_status()

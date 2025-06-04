import streamlit as st
import pandas as pd
import os

def show_offered_applicants():
    st.title("🎉 Applicants Offered a Position")

    csv_path = "parsed_data/results.csv"

    if not os.path.exists(csv_path):
        st.warning("Resume data not found.")
        return

    df = pd.read_csv(csv_path)

    # Check for required column
    if "status" not in df.columns:
        st.warning("No status column found in data.")
        return

    # Filter for offered applicants
    offered_df = df[df["status"].str.lower() == "offer sent"]

    if offered_df.empty:
        st.info("No applicants have been offered positions yet.")
        return

    for i, row in offered_df.iterrows():
        with st.expander(f"{row['name']} ({row['email']})"):
            st.write(f"📧 Email: {row.get('email', 'N/A')}")
            st.write(f"📞 Phone: {row.get('phone', 'N/A')}")
            st.write(f"📝 Status: {row.get('status', 'Offered')}")
            st.write(f"📅 Interview Date: {row.get('interview_date', 'N/A')}")
            st.write(f"⏰ Interview Time: {row.get('interview_time', 'N/A')}")
            st.write("✅ This applicant has been offered the position.")

if __name__ == "__main__":
    show_offered_applicants()

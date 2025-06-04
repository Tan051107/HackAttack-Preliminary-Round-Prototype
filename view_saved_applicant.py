import streamlit as st
import pandas as pd
import os

def show_saved_applicants():
    st.title("⭐ Saved Applicants")

    csv_path = "parsed_data/results.csv"

    if not os.path.exists(csv_path):
        st.warning("Resume data not found.")
        return

    df = pd.read_csv(csv_path)

    if "saved" not in df.columns:
        st.warning("No 'saved' status found in data.")
        return

    # Normalize boolean values
    df["saved"] = df["saved"].astype(str).str.lower() == "true"
    saved_df = df[df["saved"] == True]

    if saved_df.empty:
        st.info("No applicants have been saved yet.")
        return

    for i, row in saved_df.iterrows():
        with st.expander(f"{row['name']} ({row['email']})"):
            details = {
                "📧 Email": row.get("email", "N/A"),
                "📞 Phone": row.get("phone", "N/A"),
                "📝 Status": row.get("status", "N/A"),
                "📅 Interview Date": row.get("interview_date", "N/A"),
                "⏰ Interview Time": row.get("interview_time", "N/A")
            }
            for label, value in details.items():
                st.write(f"{label}: {value}")

if __name__ == "__main__":
    show_saved_applicants()


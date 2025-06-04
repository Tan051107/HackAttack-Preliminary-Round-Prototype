import streamlit as st
import pandas as pd
import os

RESULTS_CSV = "parsed_data/results.csv"
RESUME_FOLDER = "resumes"

def generate_suspicion_summary(row):
    reasons = []
    name = str(row['name']).lower()
    email = str(row['email']).lower()
    skills = row.get('skills', '')
    experience = str(row.get('experience', '')).lower()

    name_parts = name.split()
    if not any(part in email for part in name_parts):
        reasons.append("Email does not match name")

    if isinstance(skills, str) and len(skills.split(',')) > 20:
        reasons.append("Too many skills listed")

    buzzwords = ["top 1%", "world-class", "invented", "guru", "ninja", "rockstar", "10x", "before the internet"]
    if any(word in experience for word in buzzwords):
        reasons.append("Exaggerated claims in experience")

    return "; ".join(reasons) if reasons else "N/A"

def view_suspicious_resume():
    st.title("🚩 Suspicious Resume Dashboard")

    if not os.path.exists(RESULTS_CSV):
        st.warning("No applications found.")
        return

    df = pd.read_csv(RESULTS_CSV)

    if df.empty:
        st.info("No application data available.")
        return

    if "suspicion_flag" not in df.columns:
        st.error("No fraud detection data found. Please run detection first.")
        return

    suspicious_df = df[df["suspicion_flag"] == True].copy()

    if suspicious_df.empty:
        st.success("No suspicious resume found!")
        return

    suspicious_df["Suspicion Summary"] = suspicious_df.apply(generate_suspicion_summary, axis=1)

    st.markdown(f"### Total Suspicious Applications: {len(suspicious_df)}")

    for idx, row in suspicious_df.iterrows():
        with st.container():
            st.markdown("----")
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown("🧑‍💼")
                st.markdown(f"**Name:** {row['name']}")
                st.markdown(f"**Email:** {row['email']}")
                st.markdown(f"**Phone:** {row.get('phone', 'N/A')}")
                st.markdown(f"**Score:** {row['fraud_score']}")

            with col2:
                st.markdown(f"**Job Title:** {row['job_title']}")
                st.markdown(f"**Company:** {row.get('company', 'N/A')}")
                st.markdown(f"**Applied:** {row['application_date']}")
                st.markdown(f"**Summary:** {row['Suspicion Summary']}")
                st.markdown(f"**Skills:** {row['skills']}")
                st.markdown(f"**Experience:** {row['experience']}")

                # Show resume viewer
                resume_path = os.path.join(RESUME_FOLDER, row["filename"])
                if os.path.exists(resume_path):
                    with st.expander("📄 View Resume"):
                        st.download_button("⬇️ Download Resume", data=open(resume_path, "rb").read(), file_name=row["filename"])
                        st.markdown(f"_File: `{row['filename']}`_")
                        try:
                            st.pdf(resume_path)  # Only works in newer Streamlit versions (>=1.32)
                        except Exception as e:
                            st.info("Preview not supported in this version. Please download to view.")
                else:
                    st.error("❌ Resume file not found.")


if __name__ == "__main__":
    view_suspicious_resume()

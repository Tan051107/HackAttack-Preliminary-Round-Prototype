import streamlit as st
import pandas as pd
import os
import re
import json
from datetime import datetime
import fitz  # PyMuPDF

# --- Constants ---
JOB_CSV = "jobs_data.csv"
SKILLS_FILE = "skills.json"
RESULTS_CSV = "parsed_data/results.csv"
RESULTS_JSON = "parsed_data/results.json"
RESUME_FOLDER = "resumes"
SAVED_JOBS_CSV = "parsed_data/saved_jobs.csv"


os.makedirs("parsed_data", exist_ok=True)
os.makedirs("resumes", exist_ok=True)

# --- Utility Functions ---

def load_skills():
    if os.path.exists(SKILLS_FILE):
        with open(SKILLS_FILE, "r") as f:
            return json.load(f)
    return []

def save_skills(skills):
    with open(SKILLS_FILE, "w") as f:
        json.dump(sorted(list(set(skills))), f, indent=4)

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_name(text):
    lines = text.strip().split("\n")
    return lines[0] if lines else "Unknown"

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else "Not found"

def extract_phone(text):
    match = re.search(r'(\+?\d[\d\-\s]{8,}\d)', text)
    return match.group(0) if match else "Not found"

def extract_skills(text, known_skills):
    text_lower = text.lower()
    found = [skill for skill in known_skills if skill.lower() in text_lower]
    return list(set(found))

def save_parsed_info(data):
    # Save to CSV
    if os.path.exists(RESULTS_CSV):
        df = pd.read_csv(RESULTS_CSV)
    else:
        df = pd.DataFrame(columns=data.keys())
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(RESULTS_CSV, index=False)

    # Save to JSON
    if os.path.exists(RESULTS_JSON):
        with open(RESULTS_JSON, "r") as f:
            all_data = json.load(f)
    else:
        all_data = []
    all_data.append(data)
    with open(RESULTS_JSON, "w") as f:
        json.dump(all_data, f, indent=4)

def save_job(job_row):
    if os.path.exists(SAVED_JOBS_CSV):
        saved_df = pd.read_csv(SAVED_JOBS_CSV)
    else:
        saved_df = pd.DataFrame(columns=job_row.index)

    if not (saved_df["job_id"] == job_row["job_id"]).any():
        saved_df = pd.concat([saved_df, pd.DataFrame([job_row])], ignore_index=True)
        saved_df.to_csv(SAVED_JOBS_CSV, index=False)

def view_saved_jobs():
    st.title("📁 Saved Jobs")

    if not os.path.exists(SAVED_JOBS_CSV):
        st.info("No jobs have been saved yet.")
        return

    saved_df = pd.read_csv(SAVED_JOBS_CSV)
    if saved_df.empty:
        st.info("You haven't saved any jobs yet.")
        return

    for idx, row in saved_df[::-1].iterrows():
        st.markdown("----")
        st.subheader(f"{row['title']} ({row['job_type']})")
        st.markdown(f"**Company**: {row.get('company', 'N/A')}")
        st.markdown(f"📍 **Location:** {row['location']}")
        st.markdown(f"💰 **Salary:** {row['salary']}")
        st.markdown(f"🗓️ **Deadline:** {row['deadline']}")
        st.markdown(f"📝 **Description:** {row['description']}")
        st.markdown("**Requirements:**")
        for req in str(row['requirements']).split("; "):
            st.markdown(f"- {req}")

        with st.expander("📤 Apply to this Job"):
            resume_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"], key=f"resume_{idx}")
            if resume_file:
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{resume_file.name}"
                filepath = os.path.join(RESUME_FOLDER, filename)
                with open(filepath, "wb") as f:
                    f.write(resume_file.read())

                # Process resume
                text = fitz.open(filepath)[0].get_text()
                skills_list = []
                if os.path.exists(SKILLS_FILE):
                    with open(SKILLS_FILE, "r") as f:
                        skills_list = json.load(f)

                name = text.split('\n')[0]
                email = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
                phone = re.search(r'(\+?\d[\d\-\s]{8,}\d)', text)
                found_skills = [s for s in skills_list if s.lower() in text.lower()]
                all_skills = list(set(found_skills))

                st.success("✅ Resume processed. Review your information below:")
                st.markdown(f"**Name**: {name}")
                st.markdown(f"**Email**: {email.group(0) if email else 'Not found'}")
                st.markdown(f"**Phone**: {phone.group(0) if phone else 'Not found'}")
                st.markdown("**Skills Detected:**")
                st.write(", ".join(all_skills) if all_skills else "None detected.")

                new_skills = st.text_input("Add any missing skills (comma-separated):")
                if st.button("📨 Submit Application", key=f"submit_{idx}"):
                    extra_skills = [s.strip() for s in new_skills.split(",") if s.strip()]
                    all_skills = list(set(all_skills + extra_skills))

                    parsed_data = {
                        "name": name,
                        "email": email.group(0) if email else "Not found",
                        "phone": phone.group(0) if phone else "Not found",
                        "skills": ", ".join(all_skills),
                        "filename": filename,
                        "status": "applied",
                        "interview_date": "",
                        "interview_time": "",
                        "saved": False,
                        "company": row.get("company", "N/A"),
                        "job_id": row.get("job_id", "N/A"),
                        "job_title": row["title"],
                        "application_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    save_parsed_info(parsed_data)
                    st.success("🎉 Your application has been submitted!")


if __name__ == "__main__":
    view_saved_jobs()

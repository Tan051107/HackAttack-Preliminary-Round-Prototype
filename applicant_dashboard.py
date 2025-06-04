import streamlit as st
import pandas as pd
import os
import re
import json
from datetime import datetime
import fitz
from fuzzywuzzy import fuzz

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
    match = re.search(r"(?i)(?:Name\s*[:\-]?\s*)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", text)
    if match:
        return match.group(1).strip()
    for line in text.splitlines():
        if line.strip() and re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$', line.strip()):
            return line.strip()
    return "Unknown"

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else "Not found"

def extract_phone(text):
    match = re.search(r'(\+?\d[\d\-\s]{8,}\d)', text)
    return match.group(0) if match else "Not found"

def extract_skills(text, known_skills, threshold=80):
    text_lower = text.lower()
    found = []
    for skill in known_skills:
        score = fuzz.partial_ratio(skill.lower(), text_lower)
        if score >= threshold:
            found.append(skill)
    return list(set(found))

def extract_education(text):
    education_levels = {
        "PhD": r"\b(Ph\.?D\.?|Doctor of Philosophy)\b",
        "Master's": r"\b(M\.?Sc\.?|M\.?A\.?|Master(?:'s)? of [A-Za-z ]+)\b",
        "Bachelor's": r"\b(B\.?Sc\.?|B\.?A\.?|Bachelor(?:'s)? of [A-Za-z ]+)\b",
        "Diploma": r"\b(Diploma(?: in)? [A-Za-z &]+|Diploma)\b",
        "High School": r"\b(High School|Secondary School|H\.?S\.?)\b"
    }
    for level, pattern in education_levels.items():
        if re.search(pattern, text, re.IGNORECASE):
            return level
    return "Not found"

def extract_experience(text):
    experience_entries = re.findall(
        r'(?i)(?:Position|Title|Role)?\s*[:\-]?\s*(?P<role>[A-Z][\w\s/&]+?)\s+at\s+(?P<company>[A-Z][\w\s&]+)(?:,?\s+)?(?:from)?\s*(?P<from>\w+\s+\d{4})?\s*(?:to|-)?\s*(?P<to>\w+\s+\d{4}|Present)?',
        text
    )
    if not experience_entries:
        return "Not found"
    experiences = []
    for role, company, from_date, to_date in experience_entries:
        period = f"{from_date or '?'} - {to_date or '?'}"
        experiences.append(f"{role.strip()} at {company.strip()} ({period})")
    return "; ".join(experiences)

def save_parsed_info(data):
    if os.path.exists(RESULTS_CSV):
        df = pd.read_csv(RESULTS_CSV)
    else:
        df = pd.DataFrame(columns=data.keys())
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    df.to_csv(RESULTS_CSV, index=False)

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

def is_duplicate_application(email, job_id):
    if os.path.exists(RESULTS_CSV):
        df = pd.read_csv(RESULTS_CSV)
        return ((df['email'] == email) & (df['job_id'] == job_id)).any()
    return False

# --- Main Interface ---
def applicant_dashboard():
    st.title("🧑‍💼 Applicant Dashboard")

    if not os.path.exists(JOB_CSV):
        st.info("No jobs available.")
        return

    jobs_df = pd.read_csv(JOB_CSV)
    if jobs_df.empty:
        st.info("No job postings found.")
        return

    for idx, row in jobs_df[::-1].iterrows():
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

        if st.button("💾 Save Job", key=f"savejob_{idx}"):
            save_job(row)
            st.success("✅ Job saved successfully!")

        with st.expander("📤 Apply to this Job"):
            resume_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"], key=f"resume_{idx}")
            if resume_file:
                filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{resume_file.name}"
                filepath = os.path.join(RESUME_FOLDER, filename)
                with open(filepath, "wb") as f:
                    f.write(resume_file.read())

                text = extract_text_from_pdf(filepath)
                skills_list = load_skills()

                name = extract_name(text)
                email = extract_email(text)
                phone = extract_phone(text)
                matched_skills = extract_skills(text, skills_list)
                education = extract_education(text)
                experience = extract_experience(text)

                st.success("✅ Resume processed. You can edit the extracted details below:")

                name = st.text_input("Name", name)
                email = st.text_input("Email", email)
                phone = st.text_input("Phone", phone)
                education = st.selectbox("Education Level", ["PhD", "Master's", "Bachelor's", "Diploma", "High School", "Not found"], index=["PhD", "Master's", "Bachelor's", "Diploma", "High School", "Not found"].index(education))
                experience = st.text_area("Experience", experience)
                skills_text = st.text_input("Skills (comma-separated)", ", ".join(matched_skills))

                if st.button("📨 Submit Application", key=f"submit_{idx}"):
                    skills = [s.strip() for s in skills_text.split(",") if s.strip()]
                    if skills:
                        updated_skills = list(set(skills_list + skills))
                        save_skills(updated_skills)

                    parsed_data = {
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "skills": ", ".join(skills),
                        "education_level": education,
                        "experience": experience,
                        "filename": filename,
                        "status": "Applied",
                        "interview_date": "",
                        "interview_time": "",
                        "saved": False,
                        "company": row.get("company", "N/A"),
                        "job_id": row.get("job_id", "N/A"),
                        "job_title": row["title"],
                        "application_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

                    if is_duplicate_application(email, row.get("job_id", "N/A")):
                        st.warning("⚠️ You have already applied to this job.")
                    else:
                        save_parsed_info(parsed_data)
                        st.success("🎉 Your application has been submitted!")

    st.markdown("----")

if __name__ == "__main__":
    applicant_dashboard()

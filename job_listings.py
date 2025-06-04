import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime

CSV_FILE = "jobs_data.csv"

# ----------- Load and Save Functions ------------

def load_jobs_csv():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame(columns=[
        "job_id", "title", "description", "location", "salary",
        "job_type", "deadline", "posted_on", "requirements"
    ])

def save_jobs_csv(df):
    df.to_csv(CSV_FILE, index=False)

def save_job(job_data):
    df = load_jobs_csv()
    flat_data = job_data.copy()
    flat_data["requirements"] = "; ".join(job_data["requirements"])
    flat_data["job_id"] = str(uuid.uuid4())  # always generate new job_id
    df = pd.concat([df, pd.DataFrame([flat_data])], ignore_index=True)
    save_jobs_csv(df)

def delete_job(index):
    df = load_jobs_csv()
    df = df.drop(index).reset_index(drop=True)
    save_jobs_csv(df)

# ----------- Post Job Form ------------

def post_new_job():
    st.subheader("📌 Post a New Job")

    # Initialize default values if not in session
    if "requirements" not in st.session_state:
        st.session_state.requirements = [""]

    st.session_state.setdefault("job_title", "")
    st.session_state.setdefault("job_description", "")
    st.session_state.setdefault("job_location", "")
    st.session_state.setdefault("min_salary", 0)
    st.session_state.setdefault("max_salary", 0)
    st.session_state.setdefault("job_type", "Full-time")
    st.session_state.setdefault("deadline", datetime.today().date())

    with st.form("job_form"):
        title = st.text_input("Job Title", key="job_title")
        description = st.text_area("Job Description", key="job_description")
        location = st.text_input("Location", key="job_location")

        col1, col2 = st.columns(2)
        with col1:
            min_salary = st.number_input("Minimum Salary", min_value=0, step=100, key="min_salary")
        with col2:
            max_salary = st.number_input("Maximum Salary", min_value=0, step=100, key="max_salary")

        job_type = st.selectbox("Job Type", ["Full-time", "Part-time", "Contract", "Internship"],
                                index=["Full-time", "Part-time", "Contract", "Internship"].index(
                                    st.session_state.job_type), key="job_type")
        deadline = st.date_input("Application Deadline", key="deadline")
        posted_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        st.markdown("### 📋 Job Requirements")
        for i in range(len(st.session_state.requirements)):
            st.session_state.requirements[i] = st.text_input(f"Requirement {i + 1}",
                                                             value=st.session_state.requirements[i],
                                                             key=f"req_{i}")

        submitted = st.form_submit_button("📨 Post Job")

    if st.button("➕ Add Requirement"):
        st.session_state.requirements.append("")
        st.rerun()

    if submitted:
        valid_requirements = [r.strip() for r in st.session_state.requirements if r.strip()]
        if not title or not description or not location or not valid_requirements:
            st.warning("Please complete all fields and include at least one requirement.")
        elif min_salary > max_salary:
            st.warning("Minimum salary cannot be greater than maximum salary.")
        else:
            job_data = {
                "title": title,
                "description": description,
                "company": "IT Tech SDN BHD",
                "location": location,
                "salary": f"${min_salary:,} - ${max_salary:,}",
                "job_type": job_type,
                "deadline": str(deadline),
                "posted_on": posted_on,
                "requirements": valid_requirements
            }
            save_job(job_data)
            st.success("✅ Job saved successfully!")

            # Clear form fields
            for key in [
                "job_title", "job_description", "job_location",
                "min_salary", "max_salary", "job_type", "deadline"
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.requirements = [""]
            st.rerun()

# ----------- Display Jobs ------------

def display_jobs():
    st.subheader("📄 Posted Jobs")
    df = load_jobs_csv()

    if df.empty:
        st.info("No jobs have been posted yet.")
        return

    if "confirm_delete_index" not in st.session_state:
        st.session_state.confirm_delete_index = None

    for index, row in df[::-1].iterrows():
        real_index = row.name
        with st.container():
            st.markdown("----")
            st.markdown(f"### {row['title']} ({row['job_type']})")
            st.markdown(f"**📍 Location:** {row['location']}")
            st.markdown(f"**💰 Salary:** {row['salary']}")
            st.markdown(f"**🗓️ Deadline:** {row['deadline']}")
            st.markdown(f"**🕒 Posted On:** {row['posted_on']}")
            st.markdown(f"**📝 Description:**\n{row['description']}")
            if row.get("requirements"):
                st.markdown("**📌 Requirements:**")
                for req in str(row["requirements"]).split("; "):
                    st.write(f"- {req}")

            col1, col2 = st.columns(2)
            if col2.button("🗑️ Delete", key=f"delete_{real_index}"):
                st.session_state.confirm_delete_index = real_index

            if st.session_state.confirm_delete_index == real_index:
                st.warning(f"Are you sure you want to delete **{row['title']}**?")
                c1, c2 = st.columns([1, 1])
                if c1.button("✅ Yes, Delete", key=f"confirm_{real_index}"):
                    delete_job(real_index)
                    st.session_state.confirm_delete_index = None
                    st.success("Job deleted.")
                    st.rerun()
                if c2.button("❌ Cancel", key=f"cancel_{real_index}"):
                    st.session_state.confirm_delete_index = None

            st.markdown("----")

# ----------- Main App ------------

def job_board():
    st.title("💼 Job Management Board")
    post_new_job()
    display_jobs()

if __name__ == "__main__":
    job_board()

import streamlit as st
import pandas as pd
import re

def candidate_comparison():
    # --- Load candidate data ---
    df = pd.read_csv("parsed_data/results.csv")

    st.title("📊 Candidate Comparison")

    # --- Filter only jobs from company "IT Tech SDN BHD" ---
    company_name = "IT Tech SDN BHD"
    company_jobs_df = df[df['company'] == company_name]

    if company_jobs_df.empty:
        st.error(f"No job listings found for company '{company_name}'.")
        st.stop()

    # --- Job ID Selection for that company only ---
    job_titles = company_jobs_df[['job_id', 'job_title']].drop_duplicates()
    title_to_id = dict(zip(job_titles['job_title'], job_titles['job_id']))

    selected_job_title = st.selectbox("Select a Job Title to Compare Candidates", options=job_titles['job_title'])
    selected_job_id = title_to_id[selected_job_title]

    # --- Load job metadata ---
    try:
        job_data = pd.read_csv("jobs_data.csv")  # Path may vary depending on deployment
    except Exception as e:
        st.error(f"Failed to load job data: {e}")
        st.stop()

    # --- Get required skills for selected job ---
    if 'requirements' not in job_data.columns:
        st.error("`required_skills` column is missing in jobs_data.csv.")
        st.stop()

    job_row = job_data[job_data['job_id'] == selected_job_id]
    if job_row.empty:
        st.warning("No matching job found in jobs_data.csv.")
        st.stop()

    raw_skills = job_row.iloc[0]['requirements']
    reference_skills = set(map(str.strip, str(raw_skills).lower().split(',')))

    st.markdown(f"**🧩 Job-Specific Reference Skills:** `{', '.join(reference_skills)}`")

    # --- Education level scoring map ---
    education_score_map = {
        "PhD": 3,
        "Master's Degree": 2,
        "Bachelor's Degree": 1,
        "Diploma": 0.5,
        "High School": 0.2
    }

    # --- Scoring function ---
    def compute_score(row):
        education = str(row['education_level']).strip().title()
        education_score = education_score_map.get(education, 0)

        experience_years = 0
        if isinstance(row['experience'], str):
            match = re.search(r'(\d+)', row['experience'])
            if match:
                experience_years = int(match.group(1))
        experience_score = min(experience_years / 3, 1)  # max 1 for 3+ years

        candidate_skills = set()
        if pd.notna(row['skills']):
            candidate_skills = set(map(str.strip, str(row['skills']).lower().split(',')))
        matched_skills = candidate_skills & reference_skills
        skill_score = len(matched_skills) / len(reference_skills) if reference_skills else 0

        total_score = (0.2 * education_score) + (0.2 * experience_score) + (0.6 * skill_score)
        return round(total_score * 100, 2)

    # --- Filter candidates for selected job ID ---
    candidates = company_jobs_df[company_jobs_df['job_id'] == selected_job_id].copy()

    if candidates.empty:
        st.warning("No candidates found for the selected job.")
        st.stop()

    candidate_names = candidates['name'].tolist()

    if len(candidate_names) < 2:
        st.warning("Not enough candidates (minimum 2) for this job to compare.")
        st.stop()

    # --- Let user select exactly two candidates ---
    selected_candidates = st.multiselect(
        "Select exactly two candidates to compare",
        options=candidate_names,
        default=candidate_names[:2]
    )

    if len(selected_candidates) != 2:
        st.warning("Please select exactly two candidates to compare.")
        st.stop()

    # --- Filter and score selected candidates ---
    selected_df = candidates[candidates['name'].isin(selected_candidates)].copy()
    selected_df['score'] = selected_df.apply(compute_score, axis=1)
    selected_df = selected_df.sort_values(by="score", ascending=False)

    # --- Display the two candidates side by side ---
    st.subheader(f"🔍 Comparing Selected Candidates for Job Title: {selected_job_title}")

    cols = st.columns(2)
    for i, (_, candidate) in enumerate(selected_df.iterrows()):
        with cols[i]:
            candidate_skills = set(map(str.strip, str(candidate['skills']).lower().split(',')))
            matched_skills = candidate_skills & reference_skills
            st.markdown(f"### 👤 {candidate['name']}")
            st.markdown(f"**📈 Score:** `{candidate['score']} / 100`")
            st.markdown(f"**🎓 Education:** {candidate['education_level']}")
            st.markdown(f"**💼 Experience:** {candidate['experience']}")
            st.markdown(f"**🛠️ Skills:** {candidate['skills']}")
            st.markdown(f"**✅ Matched Skills:** {', '.join(matched_skills) if matched_skills else 'None'}`")
            st.markdown(f"**📧 Email:** {candidate['email']}")
            st.markdown(f"**📞 Phone:** {candidate['phone']}")
            st.markdown(f"**📅 Applied On:** {candidate['application_date']}")

    # --- Highlight top candidate ---
    best_candidate = selected_df.iloc[0]
    st.markdown("---")
    st.success(f"✅ **Top Candidate:** `{best_candidate['name']}` with a score of **{best_candidate['score']} / 100**")


if __name__ == "__main__":
    candidate_comparison()

import streamlit as st
import pandas as pd
import os
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def send_email(to_email, subject, body, smtp_server, smtp_port, sender_email, sender_password):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

def save_applicant(applicant_email, csv_path="parsed_data/results.csv"):
    df = pd.read_csv(csv_path)
    if "saved" not in df.columns:
        df["saved"] = False
    df.loc[df["email"] == applicant_email, "saved"] = True
    df.to_csv(csv_path, index=False)

def show_parsed_resumes():
    st.title("📄 Resume Review Dashboard")

    csv_path = "parsed_data/results.csv"
    resume_dir = "resumes"

    if not os.path.exists(csv_path):
        st.warning("No parsed resume data found.")
        return

    df = pd.read_csv(csv_path)
    company_name = "IT Tech SDN BHD"
    df = df[df["company"] == company_name]

    if df.empty:
        st.info(f"No applicants found for {company_name}.")
        return


    if "saved" not in df.columns:
        df["saved"] = False
        df.to_csv(csv_path, index=False)

    search_term = st.text_input("🔍 Search by name or email")
    if search_term:
        df = df[df["name"].str.contains(search_term, case=False, na=False) |
                df["email"].str.contains(search_term, case=False, na=False)]

    if df.empty:
        st.info("No matching resumes found.")
        return

    for idx, row in df.iterrows():
        saved_icon = "✅ Saved" if row.get("saved", False) else ""
        with st.expander(f"{row['name']} ({row['email']}) {saved_icon}"):
            st.write(f"📧 Email: {row['email']}")
            st.write(f"📌 Current Status: {row.get('status', 'Not Set')}")

            action = st.radio("Choose an action", ["View Resume", "Send Interview Invite", "Reject", "Save Applicant"], key=f"action_{idx}")

            # Resume viewer
            if action == "View Resume":
                resume_path = os.path.join(resume_dir, str(row.get("filename", "")).strip())
                if os.path.exists(resume_path):
                    with open(resume_path, "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="800" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
                else:
                    st.error(f"❌ Resume file not found: {resume_path}")

            # Interview invite
            elif action == "Send Interview Invite":
                interview_date = st.date_input("📅 Interview Date", key=f"date_{idx}")
                interview_time = st.time_input("⏰ Interview Time", key=f"time_{idx}")

                if st.button("📨 Send Interview Email", key=f"send_invite_{idx}"):
                    subject = "Interview Invitation"
                    body = f"""Dear {row['name']},

We are pleased to invite you to an interview for the position you applied for.

📅 Date: {interview_date.strftime('%A, %d %B %Y')}
⏰ Time: {interview_time.strftime('%I:%M %p')}

Please reply to confirm your availability.

Best regards,
HR Team
"""
                    try:
                        send_email(
                            to_email=row["email"],
                            subject=subject,
                            body=body,
                            smtp_server="smtp.gmail.com",
                            smtp_port=465,
                            sender_email=st.secrets["SENDER_EMAIL_ADDRESS"],
                            sender_password=st.secrets["SENDER_EMAIL_PASSWORD"]
                        )
                        df.at[idx, "status"] = "Interview Invited"
                        df.at[idx, "interview_date"] = interview_date.strftime("%Y-%m-%d")
                        df.at[idx, "interview_time"] = interview_time.strftime("%H:%M:%S")
                        df.to_csv(csv_path, index=False)
                        st.success(f"✅ Interview invite sent to {row['email']}")
                    except Exception as e:
                        st.error(f"❌ Failed to send email: {e}")

            # Rejection
            elif action == "Reject":
                if st.button("❌ Send Rejection Email", key=f"reject_{idx}"):
                    subject = "Job Application is Rejected"
                    body = f"""Dear {row['name']},

Thank you very much for your interest in our company and for taking the time to submit your application.

After careful consideration, we regret to inform you that we will not be moving forward with your application at this time. While your qualifications are impressive, we have decided to proceed with candidates whose experience more closely matches our current needs.

We appreciate your interest in our company and encourage you to apply for future openings that align with your skills and experience.

Wishing you all the best in your job search and future endeavors.

Best regards,
HR Team
"""
                    try:
                        send_email(
                            to_email=row["email"],
                            subject=subject,
                            body=body,
                            smtp_server="smtp.gmail.com",
                            smtp_port=465,
                            sender_email=st.secrets["SENDER_EMAIL_ADDRESS"],
                            sender_password=st.secrets["SENDER_EMAIL_PASSWORD"]
                        )
                        df.at[idx, "status"] = "Rejected"
                        df.to_csv(csv_path, index=False)
                        st.success(f"✅ Rejection email sent to {row['email']}")
                    except Exception as e:
                        st.error(f"❌ Failed to send email: {e}")

            # Save applicant
            elif action == "Save Applicant":
                save_applicant(row["email"])
                st.success("💾 Applicant has been saved for future reference")

if __name__ == "__main__":
    show_parsed_resumes()









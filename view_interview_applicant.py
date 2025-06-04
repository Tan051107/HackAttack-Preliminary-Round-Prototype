import streamlit as st
import pandas as pd
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email sending function
def send_email(to_email, subject, body, smtp_server, smtp_port, sender_email, sender_password):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

# Main Streamlit app
def show_invited_applicants():
    st.title("📅 Applicants Invited for Interview")

    csv_path = "parsed_data/results.csv"

    if not os.path.exists(csv_path):
        st.warning("No resume data found.")
        return

    df = pd.read_csv(csv_path)

    if "status" not in df.columns or "interview_date" not in df.columns or "interview_time" not in df.columns:
        st.warning("Interview invitation data is incomplete.")
        return

    invited_df = df[df["status"] == "Interview Invited"]

    if invited_df.empty:
        st.info("No applicants have been invited for interviews yet.")
        return

    st.subheader("Invited Applicants")

    # Load email credentials from secrets
    smtp_server = "smtp.gmail.com",
    smtp_port = 465,
    sender_email = st.secrets["SENDER_EMAIL_ADDRESS"],
    sender_password = st.secrets["SENDER_EMAIL_PASSWORD"]

    for idx, row in invited_df.iterrows():
        with st.expander(f"{row['name']} ({row['email']})"):
            st.write(f"**Interview Date:** {row['interview_date']}")
            st.write(f"**Interview Time:** {row['interview_time']}")

            col1, col2 = st.columns(2)

            # Send Offer
            with col1:
                if st.button("✅ Send Offer", key=f"offer_{idx}"):
                    df.at[idx, "status"] = "Offer Sent"
                    subject = "🎉 Job Offer from Our Company"
                    body = f"""Dear {row['name']},

We are pleased to offer you a position at our company. Congratulations!

Please reply to this email with your acceptance.

Best regards,
Recruitment Team"""
                    try:
                        send_email(row['email'], subject, body, smtp_server, smtp_port, sender_email, sender_password)
                        st.success(f"Offer sent to {row['name']} via email.")
                    except Exception as e:
                        st.error(f"Failed to send offer email: {e}")

            # Reject Applicant
            with col2:
                if st.button("❌ Reject Applicant", key=f"reject_{idx}"):
                    df.at[idx, "status"] = "Rejected"
                    subject = "Regarding Your Interview with Our Company"
                    body = f"""Dear {row['name']},

Thank you for interviewing with us. After careful consideration, we regret to inform you that you have not been selected for the position.

We appreciate your time and interest in our company.

Best wishes for your job search,
Recruitment Team"""
                    try:
                        send_email(row['email'], subject, body, smtp_server, smtp_port, sender_email, sender_password)
                        st.error(f"{row['name']} has been rejected and notified via email.")
                    except Exception as e:
                        st.error(f"Failed to send rejection email: {e}")

    # Save updates back to CSV
    df.to_csv(csv_path, index=False)

# Run the app
if __name__ == "__main__":
    show_invited_applicants()

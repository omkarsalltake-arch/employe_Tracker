


#.     / // testing mail immidiate send

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")

HR_EMAIL = os.getenv("HR_EMAIL")           # HR or test email (yahan aapka Gmail daalna hai)
SENDER_EMAIL = os.getenv("SENDER_EMAIL")   # Same as Gmail sender
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")  # Google App Password

# Connect MongoDB
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db["activity_logs"]

def generate_daily_report():
    """Fetch today's activity logs"""
    today = datetime.now().strftime("%Y-%m-%d")
    logs = collection.find({
        "timestamp": {"$regex": f"^{today}"}
    })

    report_lines = [f"📅 Daily Employee Activity Report - {today}\n"]
    report_lines.append("-----------------------------------------------------")

    for log in logs:
        line = f"👤 {log.get('employee_name', 'Unknown')} | {log.get('action')} | {log.get('timestamp')}"
        report_lines.append(line)

    if len(report_lines) == 2:
        report_lines.append("No activity logs found for today.")

    report_text = "\n".join(report_lines)
    return report_text


def send_email(report_text):
    """Send report email via Gmail SMTP"""
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = HR_EMAIL
    msg["Subject"] = f"Daily Employee Report - {datetime.now().strftime('%Y-%m-%d')}"

    msg.attach(MIMEText(report_text, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("✅ Test email sent successfully!")
    except Exception as e:
        print("❌ Failed to send email:", e)


if __name__ == "__main__":
    report = generate_daily_report()
    print("📄 Generated Report:\n")
    print(report)
    send_email(report)

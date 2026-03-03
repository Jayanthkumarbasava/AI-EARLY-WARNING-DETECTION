import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_alert(cpu, memory, disk):

    # 1️⃣ Your Gmail address
    sender_email = "basavajayanthkumar@gmail.com"

    # 2️⃣ Your 16-character app password
    sender_password = "pyrlkakoyzeqyhng"

    # 3️⃣ Receiver email
    receiver_email = "jayanth4741@gmail.com"

    # 4️⃣ Email subject
    subject = "🚨 AI Alert - High System Risk!"

    # 5️⃣ Email body
    body = f"""
    WARNING!

    High System Usage Detected.

    CPU Usage: {cpu}%
    Memory Usage: {memory}%
    Disk Usage: {disk}%

    Please take immediate action.
    """

    # 6️⃣ Create message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        # 7️⃣ Connect to Gmail server
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

        # 8️⃣ Login
        server.login(sender_email, sender_password)

        # 9️⃣ Send email
        server.send_message(message)

        # 🔟 Close connection
        server.quit()

        print("Email sent successfully!")

    except Exception as e:
        print("Email failed:", e)

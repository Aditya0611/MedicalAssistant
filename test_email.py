import smtplib
from email.mime.text import MIMEText

# Email credentials
sender_email = "adityaraj6112025@gmail.com"
password = "kjowmfcicgzkqnti"
test_recipient = input("Enter your email to test: ")

msg = MIMEText("This is a test email from the Doctor Appointment Chatbot.")
msg["Subject"] = "Test Email"
msg["From"] = sender_email
msg["To"] = test_recipient

print(f"Attempting to send test email to {test_recipient}...")

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        print("Connecting to Gmail SMTP...")
        server.login(sender_email, password)
        print("Login successful!")
        server.sendmail(sender_email, test_recipient, msg.as_string())
        print("✅ Email sent successfully!")
        print(f"Check your inbox at {test_recipient}")
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nPossible issues:")
    print("1. Gmail App Password might be invalid or expired")
    print("2. 'Less secure app access' might be disabled")
    print("3. Two-factor authentication might be required")

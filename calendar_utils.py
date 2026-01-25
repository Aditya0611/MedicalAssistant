import os
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'credentials.json'

def get_calendar_service():
    """Authenticates and returns the Google Calendar service."""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print("Warning: credentials.json not found. Calendar integration disabled.")
        return None
    
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Error authenticating with Google Calendar: {e}")
        return None

def create_appointment_event(doctor_name, patient_email, appointment_date, appointment_time):
    """Creates a Google Calendar event with Google Meet link."""
    service = get_calendar_service()
    if not service:
        return None

    try:
        # Parse date and time to datetime objects
        # appointment_date is YYYY-MM-DD
        # appointment_time is HH:MM AM/PM
        dt_str = f"{appointment_date} {appointment_time}"
        start_dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %I:%M %p")
        end_dt = start_dt + datetime.timedelta(minutes=30) # 30 min appointment

        # Convert to ISO format necessary for Google API
        # We'll assume the system local time or prompt for timezone. 
        # For simplicity, we'll use 'Asia/Kolkata' as implied by the context (India mention in code) or just UTC/Local.
        # Let's use 'Asia/Kolkata' since the user mentioned India in "Medical Info".
        time_zone = 'Asia/Kolkata' 

        event = {
            'summary': f'Appointment with {doctor_name}',
            'description': f'Doctor Appointment for {patient_email}',
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': time_zone,
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': time_zone,
            },
            'attendees': [
                {'email': patient_email},
                # We could add the doctor's email too if available in the dataset
            ],
        }

        event = service.events().insert(
            calendarId='primary', 
            body=event
        ).execute()

        print(f"Event created: {event.get('htmlLink')}")
        return True # Return success instead of link

    except Exception as e:
        error_msg = str(e)
        print(f"Error creating calendar event: {error_msg}")
        if "accessNotConfigured" in error_msg:
            return "API_DISABLED"
        return False

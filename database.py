import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)


def test_connection():
    """Tests the connection to the Supabase appointments table."""
    try:
        supabase.table("appointments").select("id").limit(1).execute()
        return True, None
    except Exception as e:
        return False, str(e)

def add_appointment(email, name, mobile, age, gender, symptoms, doctor, date, time):
    """Adds a new appointment to the database."""
    data = {
        "email": email,
        "name": name,
        "mobile": mobile,
        "age": age,
        "gender": gender,
        "symptoms": symptoms,
        "doctor": doctor,
        "appointment_date": date,
        "appointment_time": time,
    }
    try:
        response = supabase.table("appointments").insert(data).execute()
        return response
    except Exception as e:
        print(f"Error adding appointment: {e}")
        return None

def get_appointments(email):
    """Fetches appointments for a specific user email."""
    try:
        response = supabase.table("appointments").select("*").eq("email", email).execute()
        return response.data
    except Exception as e:
        print(f"Error fetching appointments: {e}")
        return []

def cancel_appointment(appointment_id):
    """Cancels an appointment by its unique ID."""
    try:
        response = supabase.table("appointments").delete().eq("id", appointment_id).execute()
        return response
    except Exception as e:
        print(f"Error cancelling appointment: {e}")
        return None

def reschedule_appointment(appointment_id, new_date, new_time):
    """Reschedules an appointment by ID."""
    try:
        update_data = {
            "appointment_date": new_date,
            "appointment_time": new_time
        }
        supabase.table("appointments").update(update_data).eq("id", appointment_id).execute()
        return True
    except Exception as e:
        print(f"Error rescheduling appointment: {e}")
        return False

def check_availability(date, time, doctor):
    """Checks if a time slot is available for a doctor."""
    try:
        print(f"DEBUG: Checking availability for {doctor} on {date} at {time}")
        # Fetch appointments for the doctor on that date
        response = supabase.table("appointments").select("*").eq("doctor", doctor).eq("appointment_date", date).execute()
        appointments = response.data
        print(f"DEBUG: Found {len(appointments)} existing appointments: {appointments}")
        
        from datetime import datetime
        new_time_dt = datetime.strptime(time, "%I:%M %p")
        
        for appt in appointments:
            booked_time = appt["appointment_time"]
            try:
                booked_time_dt = datetime.strptime(booked_time, "%I:%M %p")
                
                diff = abs((new_time_dt - booked_time_dt).total_seconds())
                print(f"DEBUG: Comparing {new_time_dt} with {booked_time_dt}. Diff: {diff} seconds")

                # Check for conflict (within 20 mins)
                if diff < 1200:
                    print("DEBUG: Conflict found!")
                    return False
            except ValueError as ve:
                print(f"DEBUG: Error parsing booked time '{booked_time}': {ve}")
                continue # Skip invalid time formats in DB
                
        print("DEBUG: Slot is available.")
        return True
    except Exception as e:
        print(f"Error checking availability: {e}")
        # Fail safe: assume available or not? Maybe blocking is safer.
        # But let's return True to not block if DB is down? No, False prevents double booking.
        return False



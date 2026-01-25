import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

try:
    print("Fetching all appointments...")
    response = supabase.table("appointments").select("*").execute()
    data = response.data

    print(f"Found {len(data)} appointments.")
    for appt in data:
        print(f"ID: {appt.get('id')} | Doctor: {appt.get('doctor')} | Date: {appt.get('appointment_date')} | Time: {appt.get('appointment_time')}")
except Exception as e:
    print("An error occurred:")
    print(e)
    if hasattr(e, 'message'):
        print(f"Message: {e.message}")
    if hasattr(e, 'details'):
        print(f"Details: {e.details}")
    if hasattr(e, 'hint'):
        print(f"Hint: {e.hint}")

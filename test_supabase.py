import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found in .env")
    exit(1)

try:
    print(f"Connecting to Supabase at {url}...")
    supabase: Client = create_client(url, key)
    
    # Try to select from appointments. If table doesn't exist, this will fail.
    print("Attempting to fetch appointments...")
    response = supabase.table("appointments").select("*").limit(1).execute()
    print("Connection successful! Table 'appointments' exists.")
    print(f"Data found: {response.data}")

except Exception as e:
    print(f"Connection failed or table missing: {e}")
    print("\n\nIMPORTANT: Please ensure you have created the 'appointments' table in your Supabase dashboard.")

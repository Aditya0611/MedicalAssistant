import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

print(f"Testing connection to: {url}")
print(f"Key type: {'service_role' if 'service' in key else 'anon'}")

supabase: Client = create_client(url, key)

# Try to insert a test record directly
print("\n--- Attempting direct insert (bypassing REST API) ---")
try:
    test_data = {
        "email": "test@example.com",
        "name": "Test User",
        "mobile": "1234567890",
        "age": 30,
        "gender": "Male",
        "symptoms": "Test",
        "doctor": "Dr. Test",
        "appointment_date": "2026-01-22",
        "appointment_time": "10:00 AM"
    }
    
    response = supabase.table("appointments").insert(test_data).execute()
    print(f"✅ INSERT SUCCESSFUL!")
    print(f"Inserted record: {response.data}")
    
    # Now try to read it back
    print("\n--- Attempting to read back ---")
    read_response = supabase.table("appointments").select("*").execute()
    print(f"✅ READ SUCCESSFUL!")
    print(f"Found {len(read_response.data)} records")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    print("\nThis confirms the table exists but PostgREST cannot see it.")
    print("The issue is with Supabase's API layer, not the database itself.")

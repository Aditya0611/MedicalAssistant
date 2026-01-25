import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

print(f"Connecting to: {url}")
print(f"Using key: {key[:20]}...")

supabase: Client = create_client(url, key)

# Try to query the appointments table
print("\n--- Testing appointments table access ---")
try:
    response = supabase.table("appointments").select("*").limit(1).execute()
    print(f"✅ SUCCESS! Table exists and is accessible.")
    print(f"Data: {response.data}")
except Exception as e:
    print(f"❌ FAILED: {e}")
    error_str = str(e)
    
    if "PGRST205" in error_str or "schema cache" in error_str:
        print("\n🔍 This error means:")
        print("   - The table doesn't exist in the database, OR")
        print("   - Row Level Security (RLS) is enabled and blocking access")
        print("\n💡 Solution:")
        print("   1. Go to Supabase Dashboard > Table Editor")
        print("   2. Check if 'appointments' table exists")
        print("   3. If it exists, click on it > RLS tab > Disable RLS (or add policies)")
        print("   4. If it doesn't exist, run the CREATE TABLE SQL again")

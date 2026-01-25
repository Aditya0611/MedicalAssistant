import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

print(f"Checking URL: {url}")

# Supabase REST API endpoint for introspecting definitions
# (This acts like checking the schema)
api_url = f"{url}/rest/v1/?apikey={key}"

try:
    print("Attempting to list tables via REST API root...")
    response = requests.get(api_url)
    
    if response.status_code == 200:
        definitions = response.json()
        print("--- Available Tables ---")
        if not definitions:
            print("No public tables found! (Did you enable RLS without adding policies?)")
        for table_name in definitions:
            print(f"- {table_name}")
    else:
        print(f"Error accessing API: Status {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"Connection error: {e}")

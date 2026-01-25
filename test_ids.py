from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

ids = ["gemini-flash-latest", "gemini-2.0-flash-lite", "gemini-2.0-flash-exp"]

for mid in ids:
    print(f"Testing ID: {mid}")
    try:
        response = client.models.generate_content(model=mid, contents="ping")
        print(f"SUCCESS with {mid}")
        break
    except Exception as e:
        print(f"FAILED with {mid}: {e}")

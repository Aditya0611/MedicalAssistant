from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

try:
    print("Listing models...")
    for model in client.models.list():
        print(f"Model Name ID: {model.name}")
except Exception as e:
    print(f"Error listing models: {e}")

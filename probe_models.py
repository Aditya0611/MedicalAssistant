from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

model_names = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-1.5-flash-002", "gemini-2.0-flash-exp", "gemini-pro"]

for name in model_names:
    print(f"Testing model: {name}")
    try:
        response = client.models.generate_content(
            model=name,
            contents="hi"
        )
        print(f"SUCCESS with {name}: {response.text}")
        break
    except Exception as e:
        print(f"FAILED with {name}: {e}")

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Set up the Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ API key not found. Make sure it's in your .env file.")
    exit()

genai.configure(api_key=api_key)

# ✅ USE THIS MODEL NAME (this works with latest SDK)
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

# ✅ This is the correct method name for this model
try:
    response = model.generate_content("Give me a healthy college breakfast idea")
    print("✅ Gemini is working!")
    print("Response:\n", response.text)
except Exception as e:
    print("❌ Gemini call failed:", e)

for model in genai.list_models():
    print(model.name, "->", model.supported_generation_methods)




import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini():
    # Load and configure API
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ API key not found in .env file")
        return False
        
    genai.configure(api_key=api_key)
    
    # List available models
    print("\nAvailable Models:")
    for model in genai.list_models():
        print(f"- {model.name}")
    
    try:
        # Test API with simple prompt
        model = genai.GenerativeModel('models/gemini-2.0-flash-lite')  # Updated model name
        response = model.generate_content("Say 'API is working!' if you can read this.")
        print("\n✅ Gemini API test successful!")
        print(f"Response: {response.text}")
        return True
    except Exception as e:
        print(f"\n❌ Gemini API test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_gemini()

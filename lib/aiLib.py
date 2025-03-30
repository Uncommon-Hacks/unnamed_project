from google import genai

GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"  # Replace with your actual API key
client = genai.Client(api_key='AIzaSyD5fpolJJg8YmzxIXPCVhbZpGNetwWhk6w')

def generate_gemini_response(prompt):
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return "Sorry, I encountered an error."
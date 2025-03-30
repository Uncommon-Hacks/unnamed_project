from google import genai
from pathlib import Path
# from markdown import markdown

GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"  # Replace with your actual API key
client = genai.Client(api_key='AIzaSyD5fpolJJg8YmzxIXPCVhbZpGNetwWhk6w')

def add_prompt_to_memory(prompt, user_id):

    custom_prompt = f'''Use the prompt given and convert it into memory paragraph
                        So the prompt given below is prompt by a user who is taling
                        to someone, and I want to store that prompt/convo as a memory
                        blob. So convert this into a memory blob for a user "{prompt}"
                        Do not add anything for prompts like "hey" or "yo" or some normal
                        conversation which cannot be converted into a memory'''
    response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents = custom_prompt
        )

    user_file = Path(__name__).parent / f"memories/{user_id}.txt"
    # Create the file if it doesn't exist
    if not user_file.exists():
        # user_file.parent.mkdir(parents=True, exist_ok=True)

        with open(user_file, 'w') as f:
            f.write(response.text)

        print("here")
    else:
        with open(user_file, 'a') as f:
            f.write(response.text)
        print("HERE")

def get_memories(user_id):

    try:
        user_file = Path(__name__).parent/f"memories/{user_id}.txt/"
        
        with open(user_file, 'r') as f:
            data = f.read()

        print("data")
    except:

        return "No memories yet for this user, respond normally"
    
    return data

def generate_gemini_response(prompt, user_id):

    data = get_memories(user_id)

    custom_prompt = f'''You have access to the following user memories, 
                        which provide context about their background, interests, 
                        projects, and ongoing challenges. Use these memories to inform your responses, 
                        ensuring relevance and personalization. Do not include or reference the memories 
                        explicitly in your reply—simply use them to enhance the conversation naturally.
                        User Memories: {data} User’s Message: “{prompt}” Respond to the user as if 
                        you have an ongoing understanding of their context, but without directly 
                        mentioning or revealing the stored memories'''
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=custom_prompt
        )
        # return markdown(response.text, extensions=["fenced_code"])
        return response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        return "Sorry, I encountered an error."
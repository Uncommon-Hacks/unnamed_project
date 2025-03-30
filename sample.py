from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import random
import os

# Initialize Gemini client
client = genai.Client(api_key='AIzaSyD5fpolJJg8YmzxIXPCVhbZpGNetwWhk6w')

# Folder to save images
output_folder = "generated_images"
os.makedirs(output_folder, exist_ok=True)

# Realistic prompt templates
prompt_templates = [
    "An ultra-realistic photo of a {adj} {noun} in a {place}, taken with a DSLR camera",
    "A photorealistic image of a {adj} {noun} near a {place}, in 8K resolution",
    "A high-resolution realistic photo of a {noun} in the {place}, with natural lighting",
    "A real-life depiction of a {adj} {noun} surrounded by {adj2} elements in a {place}"
]

adjectives = [
    "majestic", "abandoned", "ancient", "bioluminescent", "icy", "sunlit",
    "weathered", "lush", "misty", "realistic", "vivid", "textured"
]

adjectives2 = [
    "foggy", "natural", "detailed", "wet", "reflective", "dusty", "realistic"
]

nouns = [
    "mountain cabin", "robot dog", "mossy tree", "stone temple", "old car",
    "river", "wooden bridge", "waterfall", "barn", "forest animal", "train"
]

places = [
    "forest", "desert", "foggy valley", "mountain range", "coastal cliff",
    "abandoned village", "countryside", "glacier", "overgrown ruins"
]

# Compose the prompt
template = random.choice(prompt_templates)
prompt = template.format(
    adj=random.choice(adjectives),
    noun=random.choice(nouns),
    adj2=random.choice(adjectives2),
    place=random.choice(places)
)

print(f"Prompt: {prompt}")

# Generate the image
response = client.models.generate_content(
    model="gemini-2.0-flash-exp-image-generation",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_modalities=['Text', 'Image']
    )
)

# Save and display image
for part in response.candidates[0].content.parts:
    if part.text is not None:
        print("Caption/Response:", part.text)
    elif part.inline_data is not None:
        image = Image.open(BytesIO(part.inline_data.data))
        sanitized_prompt = prompt.replace(" ", "_").replace("/", "_")
        filepath = os.path.join(output_folder, f"{sanitized_prompt[:50]}_image.png")
        image.save(filepath)
        image.show()
        print(f"Image saved to: {filepath}")

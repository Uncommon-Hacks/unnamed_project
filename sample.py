from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import random
import os

# Initialize Gemini client
client = genai.Client(api_key='AIzaSyCQV43WISnhM_seEl1MD6Sg59VYXelI5Ok')

# Folder to save images
output_folder = "static/img/fake"
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
    "weathered", "lush", "misty", "realistic", "vivid", "textured",
    "rusty", "ornate", "delicate", "vibrant", "eerie", "moonlit",
    "tranquil", "frosted", "colorful", "metallic", "cracked", "haunted",
    "overgrown", "peaceful", "shimmering", "shadowy", "stormy", "tangled",
    "golden", "hollow", "silken", "hidden", "burnt", "twisted",
    "glistening", "scarred", "timeless", "cobwebbed", "emerald", "weather-beaten"
]


adjectives2 = [
    "foggy", "natural", "detailed", "wet", "reflective", "dusty", "realistic",
    "windy", "frozen", "sun-drenched", "overcast", "minimalist", "vintage",
    "muddy", "leafy", "gritty", "chaotic", "symmetrical", "shattered",
    "blooming", "graceful", "noisy", "dimly-lit", "rain-soaked", "windblown"
]

nouns = [
    "mountain cabin", "robot dog", "mossy tree", "stone temple", "old car",
    "river", "wooden bridge", "waterfall", "barn", "forest animal", "train"
]

places = [
    "forest", "desert", "foggy valley", "mountain range", "coastal cliff",
    "abandoned village", "countryside", "glacier", "overgrown ruins",
    "seaside dock", "quiet street", "field of flowers", "snowy trail",
    "train station", "deserted playground", "foggy bay", "sunset meadow",
    "suburban backyard", "boardwalk", "riverside path", "rainy alley",
    "hidden garden", "attic", "greenhouse", "underground tunnel",
    "cemetery", "chapel", "library", "market square", "cobblestone street"
]
num = int(input("How many querries? "))
for i in range(num):
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

from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64

client = genai.Client(api_key='AIzaSyDgSpcR-2o5ZsU3Ac-1RjvfXFo6QqKicCA')

contents = ('Realistic butterfly')

response = client.models.generate_content(
    model="gemini-2.0-flash-exp-image-generation",
    contents=contents,
    config=types.GenerateContentConfig(
      response_modalities=['Text', 'Image']
    )
)

for part in response.candidates[0].content.parts:
  if part.text is not None:
    print(part.text)
  elif part.inline_data is not None:
    image = Image.open(BytesIO((part.inline_data.data)))
    image.save('gemini-native-image.png')
    image.show()
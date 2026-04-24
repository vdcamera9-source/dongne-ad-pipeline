from google import genai
import os

client = genai.Client()
for m in client.models.list():
    print(m.name)

import google.generativeai as genai
import json
from core.config import settings
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-3.5-flash')
try:
  response = model.generate_content('Respond ONLY in valid JSON format with the following keys: "recommended_steps" (integer), "reason" (string). user activity history: []')
  print(repr(response.text))
except Exception as e:
  print('ERROR:', e)
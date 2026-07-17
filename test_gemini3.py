import google.generativeai as genai
from core.config import settings
genai.configure(api_key=settings.GEMINI_API_KEY)
try:
  model = genai.GenerativeModel('gemini-2.0-flash')
  response = model.generate_content('hi')
  print('SUCCESS:', response.text)
except Exception as e:
  print('ERROR:', e)
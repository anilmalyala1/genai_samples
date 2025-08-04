
import google.generativeai as generativeai
import os as os
from dotenv import load_dotenv, find_dotenv
from langchain_google_vertexai import ChatVertexAI


envfile=find_dotenv()
load_dotenv(dotenv_path=envfile)

api_key=os.getenv("API_KEY")

generativeai.configure(api_key=api_key)
model=generativeai.GenerativeModel(model_name="gemini-1.5-flash-002")
response=model.generate_content("How to use load_dotenv method in python, Share examples")

print(response.text)
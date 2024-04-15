from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv();
gptapi_key = os.getenv('GPTAPI_KEY');
client = OpenAI(
    api_key=gptapi_key, # Provide API Key in .env 
)

def call_chatgpt(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )

        message = response.choices[0].message.content.strip()
        # print("ChatGPT Response:", message) # for testing purposes
        if message != None:
            return message
        else:
            return None

    except Exception as e:
        print("An error occurred:", str(e))
        return None
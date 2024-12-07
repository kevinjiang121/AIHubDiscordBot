import os
from dotenv import load_dotenv
from openai import OpenAI
import json

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client with the API key from environment variables
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def openai_assistant_call(prompt):
    try:
        # Send a message to the thread with the user-provided prompt
        client.beta.threads.messages.create(
            thread_id=os.getenv('THREAD_ID'),
            role="user",
            content=prompt
        )

        # Create and poll a run
        run = client.beta.threads.runs.create_and_poll(
            thread_id=os.getenv('THREAD_ID'),
            assistant_id=os.getenv('ASSISTANT_ID')
        )

        # Check run status and get the response if completed
        if run.status == 'completed':
            messages = client.beta.threads.messages.list(
                thread_id=os.getenv('THREAD_ID')
            )
            last_message = messages.data[0]
            response = last_message.content[0].text.value
            return response
        else:
            print(f"Run status: {run.status}")
            return ""
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""


def get_thread_history(thread_id):
    try:
        thread_messages = client.beta.threads.messages.list(thread_id)
        thread_list = [threads.content[0].text.value for threads in thread_messages]
        print(thread_list)
    except Exception as e:
        print(f"An error occurred while fetching thread history: {e}")

def get_openai_chat_response(prompt):
    response = openai_assistant_call(prompt)
    return response
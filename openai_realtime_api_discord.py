import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('GPTAPI_KEY')

async def connect_to_openai(prompt):
    url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "realtime=v1",
    }

    async with websockets.connect(url, extra_headers=headers) as ws:
        print("Connected to OpenAI Realtime API.")

        # Send a message to the server with a custom prompt from Discord
        message = {
            "type": "response.create",
            "response": {
                "modalities": ["text"],
                "instructions": prompt,  # Pass the prompt dynamically from the bot
            }
        }
        await ws.send(json.dumps(message))

        # Wait for incoming messages from OpenAI Realtime API
        while True:
            response = await ws.recv()
            data = json.loads(response)
            
            # Check if valid response received from OpenAI
            if 'item' in data and 'text' in data['item']:
                return data['item']['text']
            else:
                return "No valid response received from OpenAI."

import asyncio
import websockets
import json
import os
from dotenv import load_dotenv
import speech_recognition as sr

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

        # Send a message to the server with the prompt
        message = {
            "type": "response.create",
            "response": {
                "modalities": ["text"],
                "instructions": prompt,
            }
        }
        await ws.send(json.dumps(message))

        # Wait for incoming messages from OpenAI Realtime API
        while True:
            response = await ws.recv()
            data = json.loads(response)
            
            # Check if valid response received from OpenAI
            if 'item' in data and 'text' in data['item']:
                print(f"OpenAI Response: {data['item']['text']}")
                break
            else:
                print("No valid response received from OpenAI.")
                break

def listen_to_microphone():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    print("Please speak into the microphone.")

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        # Use Google's speech recognition to transcribe the audio
        prompt = recognizer.recognize_google(audio)
        print(f"You said: {prompt}")
        return prompt
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return None

def main():
    prompt = listen_to_microphone()
    if prompt:
        asyncio.run(connect_to_openai(prompt))
    else:
        print("No valid prompt to send to OpenAI.")

if __name__ == "__main__":
    main()

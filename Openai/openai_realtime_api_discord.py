import os
import json
import websocket
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
headers = [
    "Authorization: Bearer " + OPENAI_API_KEY,
    "OpenAI-Beta: realtime=v1"
]

def on_open(ws):
    print("Connected to server.")
    event = {
        "type": "response.create",
        "response": {
            "modalities": ["audio", "text"],
            "model": "gpt-4o-realtime-preview-2024-12-17",
            "instructions": "You are ChatGPT. Please assist the user with their queries.",
            "voice": "alloy",
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_transcription": {
                "model": "whisper-1"
            },
        }
    }
    ws.send(json.dumps(event))

def on_message(ws, message):
    data = json.loads(message)
    try:
        outputs = data['response']['output']
        for output in outputs:
            content = output.get('content', [])
            for item in content:
                if item['type'] == 'text':
                    print("ChatGPT:", item['text'])
    except KeyError as e:
        print(f"Key error: {e}. Full data: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def on_close(ws, close_status_code, close_msg):
    print("Disconnected from server.")

def send_message(ws):
    while True:
        user_input = input("Enter your message (type 'exit' to quit): ")
        if user_input.lower() == "exit":
            ws.close()
            break
        event = {
            "type": "response.create",
            "response": {
                "modalities": ["text"],
                "instructions": user_input
            }
        }
        ws.send(json.dumps(event))

def open_websocket():
    ws = websocket.WebSocketApp(
        url,
        header=headers,
        on_open=on_open,
        on_message=on_message,
        on_close=on_close,
    )

    ws_thread = Thread(target=ws.run_forever)
    ws_thread.start()

    send_message(ws)

import base64
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv();
gptapi_key = os.getenv('GPTAPI_KEY');
client = OpenAI(
    api_key=gptapi_key, 
)

input_voice = input()

completion = client.chat.completions.create(
    model="gpt-4o-audio-preview",
    modalities=["text", "audio"],
    audio={"voice": "alloy", "format": "wav"},
    messages=[
        {
            "role": "user",
            "content": "Repeat this sentence back: " + input_voice
        }
    ]
)

print(completion.choices[0])

wav_bytes = base64.b64decode(completion.choices[0].message.audio.data)
os.makedirs("audio", exist_ok=True)

with open(os.path.join("audio", "audio.wav"), "wb") as f:
    f.write(wav_bytes)
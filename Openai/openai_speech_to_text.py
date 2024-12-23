from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
gptapi_key = os.getenv('GPTAPI_KEY')
client = OpenAI(
    api_key=gptapi_key, 
)

def call_openai_stt():
  audio_file= open("audio/audio.wav", "rb")
  transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file
  )
  return transcription.text
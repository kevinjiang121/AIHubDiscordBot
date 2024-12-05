import ComfyUI.comfyui_api_websocket_discord as comfy_api
import Openai.openai_speech_to_text as openai_stt
import Openai.openai_speech_output as openai_tts
import Openai.openai_realtime_api_discord as openai_realtime

def get_comfy_images(prompt, lora):
    return comfy_api.get_image_output(prompt, lora)

def openai_text_to_speech(input):
    openai_tts.call_open_ai_speech_output(input)

def openai_speech_to_text(file_path):
    openai_stt.call_openai_stt(file_path)

if __name__ == "__main__":
    openai_text_to_speech("Hello What's up Dog")
import ComfyUI.comfyui_api_websocket_discord as comfy_api
import Openai.openai_speech_to_text as openai_stt
import Openai.openai_speech_output as openai_tts
import Openai.openai_realtime_api_discord as openai_realtime

def get_comfy_images(prompt, lora):
    comfy_api.call_comfy_images(prompt, lora)

if __name__ == "__main__":
    get_comfy_images("Realistic","Realistic.safetensors")
import json
import random
from dotenv import load_dotenv
import random
import ComfyUI.websocket_handler as wh

load_dotenv()

# Define the path to the JSON file
json_file_path = None

# Image call
def call_comfy_images(prompt_input, lora):
    global json_file_path
    json_file_path = 'ComfyUI Layout/Realistic.json'
    input_index = get_index_of_nodes_images()
    seed_index = input_index[0]
    prompt_text_index = input_index[1]
    lora_index = input_index[2]
    seed = random.randint(0, 2_147_483_647)
    print("Image Generation Request Recieved")
    with open(json_file_path, 'r') as file:
        prompt = json.load(file)

    prompt[prompt_text_index]["inputs"]["text"] = prompt_input
    prompt[seed_index]["inputs"]["seed"] = seed
    if lora_index is not None:
        prompt[lora_index]["inputs"]["lora_name"] = lora

    images = wh.get_files(prompt)
    return images

def get_image_output(prompt_input, lora):
    images = call_comfy_images(prompt_input, lora)
    image_index = get_index_of_nodes_images()[3]
    image = images[image_index][0]
    return image

def get_index_of_nodes_images():
    seed = None
    prompt = None
    lora = None
    output = None
    
    with open(json_file_path, 'r') as file:
        input_graph = json.load(file)
    
    for index, data in input_graph.items():
        if data["class_type"] == "KSampler":
            seed = index 
        if data["_meta"]["title"] == "CLIP Text Encode (Prompt) Positive":
            prompt = index
        if data["class_type"] == "LoraLoader":
            lora = index
        if data["class_type"] == "SaveImage":
            output = index
    return seed, prompt, lora, output


# Video Call
def get_comfyui_videos(prompt_input):
    global json_file_path
    json_file_path = 'ComfyUI Layout/Video.json'
    input_index = get_index_of_nodes_video()
    video_index = input_index[1]
    noise_seed_index = input_index[0]
    seed = random.randint(0, 2_147_483_647)
    print("Video Generation Request Recieved")
    with open(json_file_path, 'r') as file:
        prompt = json.load(file)
    prompt[video_index]["inputs"]["text"] = prompt_input
    prompt[noise_seed_index]["inputs"]["noise_seed"] = seed
    video = wh.get_files(prompt)
    return video

def get_video_output(prompt_input):
    videos = get_comfyui_videos(prompt_input)
    video_output_index = get_index_of_nodes_video()[2]
    video = videos[video_output_index][0]
    return video

def get_index_of_nodes_video():
    seed = None
    video_prompt = None
    output = None
    with open(json_file_path, 'r') as file:
        input_graph = json.load(file)
    
    for index, data in input_graph.items():
        if data["_meta"]["title"] == "CLIP Text Encode (Positive Prompt)":
            video_prompt = index
        if data["_meta"]["title"] == "SamplerCustom":
            seed = index
        if data["class_type"] == "VHS_VideoCombine":
            output = index
    return seed, video_prompt, output


# Chat Call
def call_comfy_ui_chat(prompt_input):
    global json_file_path
    json_file_path = 'ComfyUI Layout/Chat.json'
    input_index = get_index_of_nodes_chat()
    seed_index = input_index[0]
    prompt_text_index = input_index[1]
    seed = random.randint(0, 2_147_483_647)
    print("Chat Generation Request Recieved")
    with open(json_file_path, 'r') as file:
        prompt = json.load(file)

    prompt[prompt_text_index]["inputs"]["text"] = prompt_input
    prompt[seed_index]["inputs"]["random_seed"] = seed

    chat = wh.get_files(prompt)
    return chat

def get_chat_output(prompt_input):
    chats = call_comfy_ui_chat(prompt_input)
    output_index = get_index_of_nodes_chat()[2]
    chat = chats[output_index][0]
    return chat

def get_index_of_nodes_chat():
    seed = None
    prompt = None
    output = None

    with open(json_file_path, 'r') as file:
        input_graph = json.load(file)
    
    for index, data in input_graph.items():
        if data["_meta"]["title"] == "Searge LLM Node":
            seed = index
            prompt = index
        if data["_meta"]["title"] == "Searge Output Node":
            output = index

    return seed, prompt, output
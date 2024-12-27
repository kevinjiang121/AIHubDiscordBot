import websocket  # NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import urllib.request
import urllib.parse
from urllib import request, parse
import random
import os
import shutil
import time
from dotenv import load_dotenv
from PIL import Image  # Import Pillow for image processing
import io  # For handling byte streams
import random

load_dotenv()

# Define the path to the JSON file
json_file_path = None
server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

# get prompt result block
def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_file(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_files(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_files = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break  # Execution is done
        else:
            continue  # Previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for node_id in history['outputs']:
        node_output = history['outputs'][node_id]
        file_output = []
        if 'images' in node_output:
            for image in node_output['images']:
                image_data = get_file(image['filename'], image['subfolder'], image['type'])
                file_output.append(image_data)
        if 'gifs' in node_output:
            for video in node_output['gifs']:
                video_data = get_file(video['filename'], video['subfolder'], video['type'])
                file_output.append(video_data)
        if 'text' in node_output:
            for chat in node_output['text']:
                chat_data = chat
                file_output.append(chat_data)
        
        output_files[node_id] = file_output

    return output_files


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

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_files(ws, prompt)
    ws.close()
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

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    video = get_files(ws, prompt)
    ws.close()
    return video

def get_video_output(prompt_input):
    videos = get_comfyui_videos(prompt_input)
    video_output_index = get_index_of_nodes_video[2]
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

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    chat = get_files(ws, prompt)
    ws.close()
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

if __name__ == "__main__":
    print(get_image_output)
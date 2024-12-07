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
json_file_path = 'ComfyUI Layout/realistic.json'
comfyui_output_folder = os.getenv('COMFYUI_OUTPUT')  # Path loaded from environment variable
destination_folder = "ComfyUi Outputs"  # Folder to move the generated images
server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

def set_layout_fuile_path(file_path):
    json_file_path = file_path

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
        output_files[node_id] = file_output

    return output_files

def call_comfy_images(prompt_input, lora):
    global json_file_path
    json_file_path = 'ComfyUI Layout/realistic.json'
    input_index = get_index_of_nodes()
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

    if not os.path.exists(comfyui_output_folder):
        os.makedirs(comfyui_output_folder)

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_files(ws, prompt)
    ws.close()
    return images

def get_comfyui_videos(prompt_input):
    global json_file_path
    json_file_path = 'ComfyUI Layout/Video.json'
    input_index = get_index_of_nodes()
    video_index = input_index[4]
    noise_seed_index = input_index[0]
    seed = random.randint(0, 2_147_483_647)
    print("Video Generation Request Recieved")
    with open(json_file_path, 'r') as file:
        prompt = json.load(file)
    prompt[video_index]["inputs"]["text"] = prompt_input
    prompt[noise_seed_index]["inputs"]["noise_seed"] = seed
    if not os.path.exists(comfyui_output_folder):
        os.makedirs(comfyui_output_folder)

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    video = get_files(ws, prompt)
    ws.close()
    return video

def get_image_output(prompt_input, lora):
    image_index = get_index_of_nodes()[3]
    images = call_comfy_images(prompt_input, lora)
    image = images[image_index][0]
    return image

def get_video_output(prompt_input):
    videos = get_comfyui_videos(prompt_input)
    video = videos["98"][0]
    return video

def save_images(images):
    for node_id in images:
        for idx, image_data in enumerate(images[node_id]):
            image = Image.open(io.BytesIO(image_data))
            filename = f"{node_id}_{idx}.png"
            output_path = os.path.join(destination_folder, filename)
            image.save(output_path)
            print(f"Image saved to {output_path}")

# Gets index of Positive input prompt, first Lora, and Seed (KSampler)
def get_index_of_nodes():
    seed = None
    prompt = None
    lora = None
    image = None
    video_prompt = None
    print(json_file_path)
    with open(json_file_path, 'r') as file:
        input_graph = json.load(file)
    
    for index, data in input_graph.items():
        if data["class_type"] == "KSampler":
            seed = index 
            prompt = data["inputs"]["positive"][0]
        if data["class_type"] == "LoraLoader":
            lora = index
        if data["class_type"] == "SaveImage":
            image = index
        if data["class_type"] == "LTXVConditioning":
            video_prompt = data["inputs"]["positive"][0]
        if data["class_type"] == "SamplerCustom":
            seed = index
    return seed, prompt, lora, image, video_prompt
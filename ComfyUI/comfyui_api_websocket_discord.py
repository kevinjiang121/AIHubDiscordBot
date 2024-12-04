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

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
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
        images_output = []
        if 'images' in node_output:
            for image in node_output['images']:
                image_data = get_image(image['filename'], image['subfolder'], image['type'])
                images_output.append(image_data)
        output_images[node_id] = images_output

    return output_images

def call_comfy_images(prompt_input, lora):
    with open(json_file_path, 'r') as file:
        prompt = json.load(file)

    prompt["3"]["inputs"]["text"] = prompt_input
    # prompt["36"]["inputs"]["lora_name"] = lora
    seed = random.randint(0, 2_147_483_647)
    prompt["5"]["inputs"]["seed"] = seed

    if not os.path.exists(comfyui_output_folder):
        os.makedirs(comfyui_output_folder)

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, prompt)
    ws.close()
    return images

def get_image_output(prompt_input, lora):
    images = call_comfy_images(prompt_input, lora)
    image = Image.open(io.BytesIO(images["17"][0]))
    return image

def save_images(images):
    for node_id in images:
        for idx, image_data in enumerate(images[node_id]):
            image = Image.open(io.BytesIO(image_data))
            filename = f"{node_id}_{idx}.png"
            output_path = os.path.join(destination_folder, filename)
            image.save(output_path)
            print(f"Image saved to {output_path}")

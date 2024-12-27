import websocket  # NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import urllib.request
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

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

def get_files(prompt):
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
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
        
    ws.close()
    return output_files
import json
from urllib import request, parse
import random
import os

# Define the path to the JSON file
json_file_path = 'ComfyUI Layout/realistic.json'

# Load the JSON data from the file
with open(json_file_path, 'r') as file:
    prompt = json.load(file)

def queue_prompt(prompt):
    p = {"prompt": prompt}
    data = json.dumps(p).encode('utf-8')
    req = request.Request("http://127.0.0.1:8188/prompt", data=data)
    request.urlopen(req)

# Modify the prompt as needed
prompt["3"]["inputs"]["text"] = input()
print(prompt)

# Queue the modified prompt
# queue_prompt(prompt)

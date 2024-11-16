import json
from urllib import request, parse
import random
import os
import shutil
import time
from dotenv import load_dotenv
from PIL import Image  # Import Pillow for image processing

load_dotenv()

# Define the path to the JSON file
json_file_path = 'ComfyUI Layout/realistic.json'
comfyui_output_folder = os.getenv('COMFYUI_OUTPUT')  # Path loaded from environment variable
destination_folder = "ComfyUi Outputs"  # Folder to move the generated images

# Ensure the destination folder exists
os.makedirs(destination_folder, exist_ok=True)

# Load the JSON data from the file
with open(json_file_path, 'r') as file:
    prompt = json.load(file)

def queue_prompt(prompt):
    """Send the prompt to ComfyUI for processing."""
    p = {"prompt": prompt}
    data = json.dumps(p).encode('utf-8')
    req = request.Request("http://127.0.0.1:8188/prompt", data=data)
    request.urlopen(req)

def get_latest_file(folder):
    """Get the latest file in a folder."""
    print(f"Scanning folder: {folder}")  # Debugging statement
    files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def copy_generated_image():
    """Copy the generated image to the destination folder."""
    # Wait for the image to be generated (adjust wait time if needed)
    time.sleep(5)  # Adjust based on expected processing time
    
    # Find the latest file in the ComfyUI output folder
    latest_image = get_latest_file(comfyui_output_folder)
    if latest_image:
        # Copy the latest image to the destination folder
        destination_path = os.path.join(destination_folder, os.path.basename(latest_image))
        shutil.copy(latest_image, destination_path)
        print(f"Copied {os.path.basename(latest_image)} to {destination_folder}")
        
        # Extract and print the seed number from the copied image
        seed = extract_seed_from_image(destination_path)
        if seed:
            print(f"Seed for {os.path.basename(latest_image)}: {seed}")
    else:
        print("No new image found in the ComfyUI output folder.")

def extract_seed_from_image(image_path):
    """Extract the seed number from image metadata."""
    try:
        with Image.open(image_path) as img:
            metadata = img.info  # Access the image metadata

            # Attempt to retrieve the seedt
            seed = json.loads(metadata.get('prompt'))["5"]["inputs"]["seed"]
            
            if seed:
                print(f"Seed found: {seed}")
                return seed
            else:
                print("Seed not found in metadata.")
                return None
    except Exception as e:
        print(f"Error extracting seed from {image_path}: {e}")
        return None

# Modify the prompt as needed
prompt["3"]["inputs"]["text"] = "realistic"
prompt["36"]["inputs"]["lora_name"] = "realistic.safetensors"

# Queue the modified prompt
queue_prompt(prompt)

# Call the copy_generated_image method
copy_generated_image()

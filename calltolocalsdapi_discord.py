import requests
import base64
from requests.exceptions import ConnectionError, HTTPError, Timeout

def generate_image(prompt):
    # Make sure to change this later to an forwarded port url
    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    payload = {
        "prompt": prompt,
        "steps": 20 # More steps = generally better iamges but slowdown
    }

    # Send the payload to the Stable Diffusion API.
    response = requests.post(url, json=payload)
    # print(response.status_code) # for testing
    print("Generating Image");
    try:
        if response.status_code == 200:
            print("Image Generated");
            print();
            r = response.json()
            image_data = base64.b64decode(r['images'][0])
            return image_data
        else:
            return None
    except Exception as e:
        print("Error " + str(e))
    return None  
import requests
import base64
from requests.exceptions import ConnectionError, HTTPError, Timeout

def generate_image(prompt):
    # Define the URL and the payload to send.
    url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
    payload = {
        "prompt": prompt,
        "steps": 20  # Adjust the number of steps as necessary
    }

    # Send the payload to the Stable Diffusion API.
    response = requests.post(url, json=payload)
    print("Generating Image");
    try:
        if response.status_code == 200:
            print("Image Generated");
            print();
            r = response.json()
            # Decode the image.
            image_data = base64.b64decode(r['images'][0])
            return image_data
        else:
            return None
    except ConnectionError:
        print("Image Generator Offline.")
    except HTTPError as e:
        print(f"Image Generator Offline.")
    except Timeout:
        print("Image Generator Offline.")
    except Exception as e:
        print("Image Generator Offline.")
    return None  # Return None or an appropriate error value/message
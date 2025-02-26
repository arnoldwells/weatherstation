def getimg(summary):                                                                    # create image with getimg.ai
    import os
    import json
    import base64
    import random
    import string
    import logging
    import requests
    import datetime
    from requests.exceptions import RequestException
    from data.env import GETIMGAI_URL
    from data.config import GETIMGAI_API_KEY

    logger = logging.getLogger(__name__)                                                # logging.basicConfig(filename='/tmp/myapp.log', level=logging.INFO, format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    month = datetime.datetime.now().strftime("%B")
    date = datetime.datetime.now().strftime("%Y-%m-%d")
                                              
    # generation_endpoint = '/stable-diffusion-xl/text-to-image'                        # Endpoint for generating images $0.00030 Prices displayed are for 1M pixel steps
    generation_endpoint = '/stable-diffusion/text-to-image'                             # Endpoint for generating images $0.00045 Prices displayed are for 1M pixel steps
    logger.debug(f"received summary: {summary}")

    try:                                                                                # select artist from file
        with open("data/artists.json", "r") as fp:
            artists_dict = json.load(fp)
        artist_key = random.choice(list(artists_dict.keys()))
        artist_name = artists_dict[artist_key]["Name"]
        keywords = random.choice(artists_dict[artist_key]["Keywords"])
        if keywords != " ": keywords = f"featuring some {keywords}"
        # keywords = random.choices(artists_dict[artist_key]["Keywords"], weights=artists_dict[artist_key]["Weights"], k=1) # relative weights
        logger.info(f"Chosen artist is {artist_name} who's key is {artist_key} and whose keywords are: {keywords}")
    except:
        logger.error("Cannot process artists.json")
        return "images/getimgai-json.png"                                               # terminate the scipt

    headers = {                                                                         # Define the headers with authentication
        "Authorization": f"Bearer {GETIMGAI_API_KEY}",
        "Content-Type": "application/json",
    }

    generation_data = {                                                                 # Define the JSON data for generating the image
        "model": "absolute-reality-v1-6",                                               # Replace with desired model
        "prompt": f"Painting in the style of artist {artist_name} depicting {summary} in {month}, {keywords}",        # prompt for generating the image
        "negative_prompt": "Disfigured, cartoon, blurry, nude, frame",
        "output_format": "jpeg",                                                        # Specify JPEG format
        "width": 576,                                                                   # desired width x 64
        "height": 448,                                                                  # desired height
        "steps": 25,
        "guidance": 6                                                                   # 0-20 Higer guidance forces the model to better follow the prompt, 
    }                                                                                   # but result in lower quality output.
    if artist_key == "vangogh": generation_data["model"] = "van-gogh-diffusion"         # exceptions
    elif artist_key == "murakami": generation_data["guidance"] = 3

    try:                                                                                # Make a POST request to generate the image
        response = requests.post(f"{GETIMGAI_URL}{generation_endpoint}", 
                                 headers=headers, 
                                 json=generation_data)
        response.raise_for_status()

        response_data = response.json()                                                 # Parse the response JSON for the generated image
        image_bytes = base64.b64decode(response_data['image'])                          # Decode the base64 image string

        generation_data.update({'seed': response_data['seed'], 
                                'cost': response_data['cost']})

        suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=2))     # Generate a random string for uniqueness
        filename = f"{date}-{artist_key}-{suffix}.jpg"                                  # Construct the filename with date, artist and random string
        file_path = os.path.join('generated', filename)                                 # Specify the file path for saving the generated image
        os.makedirs('generated', exist_ok=True)

        with open(file_path, 'wb') as image_file:                                       # Save the generated image to the specified file path
            image_file.write(image_bytes)

        logger.info(f"Image generated successfully and saved as '{file_path}'")

        """ to do: delete old images if they exist """

        with open("data/image-metadata.json", "w") as fp:
            json.dump(generation_data, fp)                                              # encode dict into JSON
        return [(file_path, "artimage")]                                                # success

    except RequestException as e:
        logger.error(f"Error generating image : {e.response.status_code}")
        logger.error(e.response.text)

        if e.response.status_code in [400, 401, 402, 404, 429, 500]:        
            error_file = f"images/getimgai{e.response.status_code}.png"
            return [(error_file, "artimage")]        

    except Exception as e:
        logger.error(f"Request error: {e}")
        
    return [("images/getimgai.png", "artimage")]

if __name__ == "__main__":
    print("should be run from main.py")

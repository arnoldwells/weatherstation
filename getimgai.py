def getimg(summary):
    import os
    import json
    import base64
    import random
    import string
    import requests
    import datetime
    from config import GETIMGAI_API_KEY
    from constants import DEBUG, GETIMGAI_URL

    month = datetime.datetime.now().strftime("%B")
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    
                                              
    # generation_endpoint = '/stable-diffusion-xl/text-to-image'                                    # Endpoint for generating images $0.00030 Prices displayed are for 1M pixel steps
    generation_endpoint = '/stable-diffusion/text-to-image'                                         # Endpoint for generating images $0.00045 Prices displayed are for 1M pixel steps
    if DEBUG: print("received summary:", summary)

    try:                                                                                            # select artist from file
        with open("artists-new.json", "r") as fp:
            artists_dict = json.load(fp)
        if DEBUG: print(artists_dict, "\n")
        artist_key = random.choice(list(artists_dict.keys()))
        artist_name = artists_dict[artist_key]["Name"]
        keywords = random.choice(artists_dict[artist_key]["Keywords"])
        # keywords = random.choices(artists_dict[artist_key]["Keywords"], weights=artists_dict[artist_key]["Weights"], k=1) # relative weights
        if DEBUG: print(f"Chosen artist is {artist_name} whos key is {artist_key} and whose keywords are: {keywords}")
    except:
        print("Cannot process artists-new.json")
        return "images/getimgai-json.png"                                                           # terminate the scipt

    headers = {                                                                                     # Define the headers with authentication
        'Authorization': f'Bearer {GETIMGAI_API_KEY}',
        'Content-Type': 'application/json',
    }

    generation_data = {                                                                             # Define the JSON data for generating the image
        # "model": "stable-diffusion-xl-v1-0",                                                      # Replace with your desired model
        "model": "absolute-reality-v1-6",                                                           # Replace with your desired model
        "prompt": f"{summary} in {month}. {keywords}. Painting in the style of artist {artist_name}",        # Your prompt for generating the image
        "negative_prompt": "Disfigured, cartoon, blurry, nude",
        "output_format": "jpeg",                                                                    # Specify JPEG format
        "width": 576,                                                                               # Your desired width x 64
        "height": 448,                                                                              # Your desired height
        "steps": 25,
        "guidance": 6                                                                               # 0-20 Higer guidance forces the model to better follow the prompt, 
    }                                                                                               # but result in lower quality output.
    if artist_key == "vangogh":                                                                     # exceptions
        generation_data["model"] = "van-gogh-diffusion"
    elif artist_key == "murakami":
        generation_data["guidance"] = 3

    try:                                                                                            # Make a POST request to generate the image
        response_generation = requests.post(f'{GETIMGAI_URL}{generation_endpoint}', headers=headers, json=generation_data)
        
        if response_generation.status_code == 200:                                                  # Check if the generation request was successful (status code 200)
            
            generated_data = response_generation.json()                                             # Parse the response JSON for the generated image
            generated_image_data = base64.b64decode(generated_data['image'])                        # Decode the base64 image string
            generation_data['seed'] = generated_data['seed']
            generation_data['cost'] = generated_data['cost']

            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=2))      # Generate a random string for uniqueness
            filename = date + '-' + artist_key + '-' + random_string + '.jpg'                       # Construct the filename with date, artist and random string
            generated_file_path = os.path.join('generated', filename)                               # Specify the file path for saving the generated image

            with open(generated_file_path, 'wb') as generated_image_file:                           # Save the generated image to the specified file path
                generated_image_file.write(generated_image_data)

            if DEBUG: print(f"Image generated successfully and saved as '{generated_file_path}'")

            """ to do: delete yesterday's image if exists """

            with open("file_metadata.json", "w") as fp:
                json.dump(generation_data, fp)                                                      # encode dict into JSON
            return generated_file_path
        else:                                                                                       # Handle error cases for generation
            print(f'Error generating image : {response_generation.status_code}')
            print(response_generation.text)
            if response_generation.status_code in [400, 401, 402, 404, 429, 500]:        
                return f"images/getimgai{response_generation.status_code}.png"
        
    except requests.exceptions.RequestException as e:                                               # Handle connection errors or other exceptions here
        print(f'Error: {e}')
    return "images/getimgai.png"

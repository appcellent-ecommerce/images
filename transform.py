import os
import requests
import base64
import glob

# Define remove.bg API
REMOVE_BG_API_KEY = 'YOUR_REMOVE_BG_API'
REMOVE_BG_API_URL = 'https://api.remove.bg/v1.0/removebg'

# Define TinyJPG API
TINY_API_KEY = 'YOUR_TINY_API'
TINY_API_URL = 'https://api.tinify.com/shrink'

def remove_background(image_data):
    response = requests.post(
        REMOVE_BG_API_URL,
        files={'image_file': image_data},
        data={'size': 'auto'},
        headers={'X-Api-Key': REMOVE_BG_API_KEY},
    )

    if response.status_code != requests.codes.ok:
        print("Error during background removal:", response.status_code, response.text)
        return None

    return response.content

def compress_image(image_data):
    headers = {
        'Authorization': 'Basic ' + base64.b64encode(('api:' + TINY_API_KEY).encode()).decode(),
    }
    response = requests.post(TINY_API_URL, data=image_data, headers=headers)
    return requests.get(response.json()['output']['url']).content

def save_image(data, filename):
    path = os.path.join('images_converted', filename)
    with open(path, 'wb') as f:
        f.write(data)

def process_images(input_folder):
    # For each file in the input folder
    for input_file in glob.glob(os.path.join(input_folder, '*')):
        # Prepare the output file name
        filename = os.path.splitext(os.path.basename(input_file))[0]
        output_file_name = filename.replace(' ', '_').lower() + '.png'  # replace spaces with "_" and lowercase

        # Skip if the file has already been converted
        if os.path.exists(os.path.join('images_converted', output_file_name)):
            print(f'Skipping already converted file: {input_file}')
            continue

        print(f'Processing image: {input_file}')

        # Compress the image
        print('Compressing image...')
        try:
            with open(input_file, 'rb') as img_file:
                compressed_img_data = compress_image(img_file.read())
            if not compressed_img_data:
                print('Failed to compress image.')
                continue
        except Exception as e:
            print(f"Error during image compression for {input_file}: {e}")
            continue

        # Remove background
        print('Removing background...')
        no_bg_img = remove_background(compressed_img_data)
        if no_bg_img is None:
            continue

        # Compress the image again
        print('Compressing image again...')
        try:
            compressed_no_bg_img = compress_image(no_bg_img)
        except Exception as e:
            print(f"Error during second image compression for {input_file}: {e}")
            continue

        # Save the image
        print('Saving image...')
        save_image(compressed_no_bg_img, output_file_name)

        print(f'Finished processing image: {input_file}\n')

# Specify the folder containing the images to be converted
process_images('images_not_converted')

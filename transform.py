import os
import requests
import base64
import glob
import argparse
from tqdm import tqdm

# Define remove.bg API
REMOVE_BG_API_KEY = 'REMOVE_BG_API'
REMOVE_BG_API_URL = 'https://api.remove.bg/v1.0/removebg'

# Define TinyJPG API
TINY_API_KEY = 'TINY_API'
TINY_API_URL = 'https://api.tinify.com/shrink'

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description='Process some images.')
parser.add_argument('--compress', action='store_true',
                    help='only compress the image')
parser.add_argument('--remove-bg', action='store_true',
                    help='only remove the background')
parser.add_argument('--output-path', type=str, default='images_converted',
                    help='path to save the processed images')
args = parser.parse_args()

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
    path = os.path.join(args.output_path, filename)
    with open(path, 'wb') as f:
        f.write(data)

def process_images(input_folder):
    # Get the list of all files in the input folder
    files = list(glob.glob(os.path.join(input_folder, '*')))

    # For each file in the input folder
    with tqdm(total=len(files), desc="Processing images", unit="image") as pbar:
        for input_file in files:
            # Prepare the output file name
            filename = os.path.splitext(os.path.basename(input_file))[0]
            output_file_name = filename.replace(' ', '_').lower() + '.png'  # replace spaces with "_" and lowercase

            # Skip if the file has already been converted
            if os.path.exists(os.path.join(args.output_path, output_file_name)):
                print(f'Skipping already converted file: {input_file}')
                pbar.update()
                continue

            with open(input_file, 'rb') as img_file:
                image_data = img_file.read()

            if args.compress:
                pbar.set_description(f"Compressing {output_file_name}")
                try:
                    compressed_img_data = compress_image(image_data)
                    if not compressed_img_data:
                        print('Failed to compress image.')
                        pbar.update()
                        continue
                    save_image(compressed_img_data, output_file_name)
                except Exception as e:
                    print(f"Error during image compression for {input_file}: {e}")
                    pbar.update()
                    continue

            elif args.remove_bg:
                pbar.set_description(f"Removing background {output_file_name}")
                no_bg_img = remove_background(image_data)
                if no_bg_img is None:
                    pbar.update()
                    continue
                save_image(no_bg_img, output_file_name)

            else:
                pbar.set_description(f"Compressing and removing background {output_file_name}")
                try:
                    compressed_img_data = compress_image(image_data)
                    if not compressed_img_data:
                        print('Failed to compress image.')
                        pbar.update()
                        continue
                except Exception as e:
                    print(f"Error during image compression for {input_file}: {e}")
                    pbar.update()
                    continue

                no_bg_img = remove_background(compressed_img_data)
                if no_bg_img is None:
                    pbar.update()
                    continue

                try:
                    final_img = compress_image(no_bg_img)
                except Exception as e:
                    print(f"Error during second image compression for {input_file}: {e}")
                    pbar.update()
                    continue

                save_image(final_img, output_file_name)

            pbar.update()

# Specify the folder containing the images to be converted
process_images('images_not_converted')

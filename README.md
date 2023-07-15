## image
1. search folder for images (images_not_converted)
2. compress image (over tinyjpg api)
3. remove background (remove.bg)
4. compress image again (tinyjpg api)
5. save the image and format the filename (images_converted)

## cli
# compress only
python transform.py --compress
# remove bg only
--remove-bg
# output path for the converted images
--output-path


## run script
python transform.py

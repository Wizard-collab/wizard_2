# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This module is used to manage images in wizard

# Python modules
import pyautogui
from PIL import Image
import io

def screenshot():
	# Capture the screen
	# Divide the image size by ≈3
	# Convert the image to bytes and return it
	image = pyautogui.screenshot()
	image = resize_image(image, 500)
	stream = io.BytesIO()
	image.save(stream, format="JPEG")
	imagebytes = stream.getvalue()
	return imagebytes

def convert_image_to_bytes(image_file, resize=100):
	# Resize the given file to 100*100
	# and return the jpg bytes
	image = Image.open(image_file)
	image = resize_image(image, resize)
	stream = io.BytesIO()
	image.save(stream, format="PNG")
	imagebytes = stream.getvalue()
	return imagebytes

def resize_image(image, fixed_height):
	height_percent = (fixed_height / float(image.size[1]))
	width_size = int((float(image.size[0]) * float(height_percent)))
	image = image.resize((width_size, fixed_height), Image.ANTIALIAS)
	return image
	
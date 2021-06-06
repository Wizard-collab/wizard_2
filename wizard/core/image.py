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
	ratio = 0.3
	image = image.resize( [int(ratio * s) for s in image.size], Image.ANTIALIAS )
	stream = io.BytesIO()
	image.save(stream, format="JPEG")
	imagebytes = stream.getvalue()
	return imagebytes

def convert_profile_picture(image_file):
	# Resize the given file to 100*100
	# and return the jpg bytes
	image = Image.open(image_file)
	fixed_height = 100
	height_percent = (fixed_height / float(image.size[1]))
	width_size = int((float(image.size[0]) * float(height_percent)))
	image = image.resize((width_size, fixed_height), Image.NEAREST)
	stream = io.BytesIO()
	image.save(stream, format="PNG")
	imagebytes = stream.getvalue()
	return imagebytes

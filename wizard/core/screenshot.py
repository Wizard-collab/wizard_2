# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import pyautogui
from PIL import Image
import io

def screenshot_to_bytes():
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
# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This module is used to manage images in wizard

# Python modules
import pyautogui
from PIL import Image, ImageCms, ImageFont, ImageDraw
import io
import base64
import random
import json
import colorsys
import os

# Wizard modules
from wizard.core import tools

def screenshot(file, thumbnail_file):
    # Capture the screen
    # Divide the image size by ≈3
    base_image = pyautogui.screenshot()
    image = resize_image(base_image, 1000)

    thumbnail, null, null = resize_image_with_fixed_width(base_image, 200)

    save_file = tools.get_filename_without_override(file)
    save_thumbnail_file = tools.get_filename_without_override(thumbnail_file)

    image.save(save_file, format="PNG")
    thumbnail.save(save_thumbnail_file, format="JPEG")
    return save_file, save_thumbnail_file

def convert_image_to_bytes(image_file, resize=100):
    # Resize the given file to 100*100
    # and return the png bytes
    image = Image.open(image_file)
    convert_PILLOW_image_to_bytes(iamge, resize)

def convert_PILLOW_image_to_bytes(image, resize=100):
    image = resize_image(image, resize)
    icc = image.info.get('icc_profile', '')
    if icc:
        icc_io_handle = io.BytesIO(icc)
        src_profile = ImageCms.ImageCmsProfile(icc_io_handle)
        dst_profile = ImageCms.createProfile('sRGB')
        image = ImageCms.profileToProfile(image, src_profile, dst_profile)
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    imagebytes = stream.getvalue()
    return imagebytes

def convert_screenshot(image_file, resize=300):
    # Resize the given file to 100*100
    # and return the png bytes
    image = Image.open(image_file)
    image, width, height = resize_image_with_fixed_width(image, resize)
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    imagebytes = stream.getvalue()
    return imagebytes, width, height

def convert_image_to_str_data(image_file, resize=100):
    encoded = base64.b64encode(convert_image_to_bytes(image_file, resize)).decode('ascii')
    return encoded

def convert_str_data_to_image_bytes(str_data):
    return base64.b64decode(str_data)

def resize_image(image, fixed_height):
    height_percent = (fixed_height / float(image.size[1]))
    width_size = int((float(image.size[0]) * float(height_percent)))
    image = image.resize((width_size, fixed_height), Image.ANTIALIAS)
    return image

def resize_image_with_fixed_width(image, fixed_width):
    width_percent = (fixed_width / float(image.size[0]))
    height_size = int((float(image.size[1]) * float(width_percent)))
    image = image.resize((fixed_width, height_size), Image.ANTIALIAS)
    return image, fixed_width, height_size
    
def project_random_image(project_name):
    letter = project_name[0].upper()
    hue = random.randint(0,100)/100.0
    saturation = random.randint(10,50)/100.0
    value = random.randint(80,90)/100.0
    rgb_tuple = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(hue,saturation,value))
    img = Image.new('RGB', (500, 282), color = rgb_tuple)

    draw = ImageDraw.Draw(img)
    circle_rgb_tuple = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(hue,saturation,value+0.04))
    draw.ellipse(((500-500)/2, (282-500)/2, (500+500)/2, (282+500)/2), fill=circle_rgb_tuple, width=0)
    circle_rgb_tuple = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(hue,saturation,value+0.08))
    draw.ellipse(((500-350)/2, (282-350)/2, (500+350)/2, (282+350)/2), fill=circle_rgb_tuple, width=0)
    circle_rgb_tuple = tuple(round(i * 255) for i in colorsys.hsv_to_rgb(hue,saturation,value+0.12))
    draw.ellipse(((500-200)/2, (282-200)/2, (500+200)/2, (282+200)/2), fill=circle_rgb_tuple, width=0)
    
    font = ImageFont.truetype("ressources/fonts/Poppins-Black.ttf", 100)
    w, h = draw.textsize(letter, font=font)
    draw.text(((500-w)/2,(282-h-30)/2), letter, (255, 255, 255), font=font)

    #img_file = os.path.join(tools.temp_dir(),'temp_img.png')
    #img.save(img_file)
    return convert_PILLOW_image_to_bytes(img, 500)
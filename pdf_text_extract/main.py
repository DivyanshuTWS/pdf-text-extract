import io
from itertools import chain
from pathlib import Path
import time
import os
import json
# import fitz <TODO> fix import error
import cv2
import numpy as np
from PIL import Image
from dotenv import load_dotenv


load_dotenv()
api_path = os.getenv("AZURE_COGNITIVE_API_PATH")
subscription_key = os.getenv("AZURE_COGNITIVE_API_KEY")

def load_config(config_path):
    if os.path.exists(config_path):
        with open(config_path, mode="r", encoding="utf-8") as f:
            return json.load(f)
    else:
        if not os.path.exists("config"):
            os.mkdir("config")    
        return None

class FileManager:
    
    def __init__(self, source_file_path:list, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.source_file_path = source_file_path


    def generate_files(self, extensions):
        files = chain(*(Path(path).glob(f'**/*.{ext}') for path in self.source_file_path for ext in extensions))
        return files
    
    
config_path = "configs/config.json"
config = load_config(config_path)

start_time =  time.ctime(time.time())
print("Program started at " + start_time)

img_source_path = config.get('img_source_path',[])
extensions = config.get("extensions", ('pdf', 'png', 'jpg'))


file_manager = FileManager(source_file_path=img_source_path, )
files = file_manager.generate_files(extensions=extensions)
for file in files:
    print(file)
    # if file.suffix == ".pdf":
    #     doc = fitz.open(file)
    #     for page in doc:
    #         pix = page.get_pixmap()
    #         img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    #         img.save(file.stem + ".png")
    # elif file.suffix == ".png" or file.suffix == ".jpg":
    #     img = cv2.imread(str(file))
    #     cv2.imwrite(file.stem + ".png", img)
    
    # method 1: 
    # send into ocr
    # post-process ocr output
    
    
    # method 2:
    # send into azure open ai
    

import io
from itertools import chain
from pathlib import Path
import time
import os
import json
import fitz
import cv2
import numpy as np
from PIL import Image
from dotenv import load_dotenv

from utils.ocr import draw_text_boxes_on_img, get_azure_object, get_word_properties_from_azure_json
import pandas as pd


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
save_img = config.get("save_img", False)
file_manager = FileManager(source_file_path=img_source_path, )
files = file_manager.generate_files(extensions=extensions)

rows = []
for file in files:
    print(file)
    img = cv2.imread(str(file))
   
    # method 1: 
    # send into ocr
    # post-process ocr output
    # send text to ocr
    ocr_result = get_azure_object(image = img, file_name=file.name, config= config, save_to_file=True)
    word_properties = get_word_properties_from_azure_json(ocr_result)
    if save_img:
        output_img = draw_text_boxes_on_img(image = img, word_properties = word_properties)
        img_save_path = "output\image\ocr"
        os.makedirs(img_save_path, exist_ok=True)
        cv2.imwrite(os.path.join(img_save_path, f'{file.stem}_ocr.png'), output_img)
    
    all_texts = " ".join([word['word_cluster'] for word in word_properties])
    rows.append(
        {"file_path": str(file.absolute()),"file_name": file.name, "text": all_texts}
    )
    
    
    # method 2:
    # send into azure open ai

df = pd.DataFrame(rows)
df.to_csv("output/pocresult.csv", index=False, encoding='utf-8')
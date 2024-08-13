# import io
from itertools import chain
from pathlib import Path
import time
import os
import json
# import fitz
import cv2
# import numpy as np
# from PIL import Image
from dotenv import load_dotenv

from utils.llm import text_to_llm
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
        print(f"Config file not found at {config_path}. Using default configuration.")
        return {}  # Return an empty dictionary instead of None



class FileManager:
    
    def __init__(self, source_file_path:list, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.source_file_path = source_file_path


    def generate_files(self, extensions):
        files = chain(*(Path(path).glob(f'**/*.{ext}') for path in self.source_file_path for ext in extensions))
        return files
    
    
config_path = r"pdf_text_extract\config.json"
config = load_config(config_path)

start_time = time.ctime(time.time())
print("Program started at " + start_time)

img_source_path = config.get('img_source_path', [])
extensions = config.get("extensions", ('pdf', 'png', 'jpg'))
save_img = config.get("save_img", False)
file_manager = FileManager(source_file_path=img_source_path)
files = file_manager.generate_files(extensions=extensions)

rows = []
for file in files:
    print(file)
    img = cv2.imread(str(file))
    
    # Check image dimensions
    height, width, _ = img.shape
    if height < 50 or width < 50 or height > 10000 or width > 10000:
        print(f"Skipping {file} due to invalid dimensions: {width}x{height}")
        continue
    
    # Proceed with OCR
    try:
        ocr_result = get_azure_object(image=img, file_name=file.name, config=config, save_to_file=True)
        word_properties = get_word_properties_from_azure_json(ocr_result)
    except Exception as e:
        print(f"Failed to process {file}. Error: {e}")
        continue

    if save_img:
        output_img = draw_text_boxes_on_img(image=img, word_properties=word_properties)
        img_save_path = "output"
        os.makedirs(img_save_path, exist_ok=True)
        cv2.imwrite(os.path.join(img_save_path, f'{file.stem}_ocr.png'), output_img)
    
    all_texts = " ".join([word['word_cluster'] for word in word_properties])
    
    llm_response = text_to_llm(output_data=all_texts)
    
    rows.append(
        {"file_path": str(file.absolute()), "file_name": file.name, "text": all_texts, "llm_text": llm_response.choices[0].message.content}
    )
df = pd.DataFrame(rows)
df.to_csv("output/pocresult.csv", index=False, encoding='utf-8')
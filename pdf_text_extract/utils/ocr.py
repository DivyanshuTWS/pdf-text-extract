import io
import json
import logging
import os
import time
from typing import Dict
import cv2
import numpy as np
import requests
from PIL import Image

def cache_file_exists(save_path: str) -> bool:
    return os.path.exists(save_path)

def load_from_cache(save_path: str) -> Dict:
    with open(save_path, "r") as f:
        return json.load(f)

def save_azure_json_to_file(json_object, file_name, dest_dir="ocr/azure"):
    """
    Save Raw Azure JSON file after running OCR
    :param json_object:
    :param file_name:
    :return:
    """ 

    dest_path = os.path.join(dest_dir, f"{file_name}.json")
    os.makedirs(dest_dir, exist_ok=True)
    # with open(get_azure_json_save_file_path(pdf_path), 'w') as fp:
    with open(dest_path, 'w') as fp:
        fp.write(json.dumps(json_object, indent=4))
        
def get_azure_object(image, file_name, config, save_to_file=False, original_file_path=None, use_cache=True, ):
    """
    Get the OCR text throught Azure engine

    Parameters
    ------
    image: object| np.ndarray
        Accepts an image object
    use_cache: bool
        To prevent from consuming credits again for the same image
        file when developing, set `use_cache` as True.
        Otherwise, if you want to use Azure to detect text again, set it as False.
    Return
    ------
        data: json

    """
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    # azure_save_file_path = get_azure_json_save_file_path(original_file_path)
    save_path = config.get("save_path", "")
    azure_save_dir_path = os.path.join(save_path, "ocr/azure")
    os.makedirs(azure_save_dir_path, exist_ok=True)
    azure_save_file_path = os.path.join(azure_save_dir_path, f"{file_name}.json") 

    if use_cache and cache_file_exists(azure_save_file_path):
        return_object = load_from_cache(azure_save_file_path)
        # logger.info(f"Using cached Azure JSON file: {azure_save_file_path}")
        return return_object

    api_path = os.getenv("AZURE_COGNITIVE_API_PATH")
    subscription_key = os.getenv("AZURE_COGNITIVE_API_KEY")

    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'content-type': 'application/octet-stream'
    }

    image_buffer = io.BytesIO()
    image.save(image_buffer, format='PNG')
    binary_data = image_buffer.getvalue()

    response = requests.post(api_path, headers=headers, data=binary_data, timeout= 60)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 202:
        url = response.headers['Operation-Location']
        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key,
        }
        return_object = requests.get(url, headers=headers, timeout= 60).json()
        while 1:
            if 'status' in return_object and return_object['status'] == 'running':
                time.sleep(1)
                return_object = requests.get(url, headers=headers, timeout= 60).json()
            else:
                if save_to_file:
                    save_azure_json_to_file(return_object, file_name, azure_save_dir_path) 
                return return_object
    else:
        logging.error(f"Failed to get image converted to text. "
                      f"Error Details: {response.text} Error Code: {response.status_code}")


def convert_to_xy_tuple(coordinates):
    """
    Convert the coordinates from the format [x, y, x, y, x, y, x, y] to [(x, y), (x, y), (x, y), (x, y)]
    :param coordinates:
    :return:
    """
    # Create an empty list to store the tuples
    tuples = []
    # Loop through the coordinates list with a step of 2
    for i in range(0, len(coordinates), 2):
        # Get the x and y values at the current index and the next index
        x = coordinates[i]
        y = coordinates[i + 1]
        # Create a tuple of (x,y) and append it to the tuples list
        tuples.append((x, y))
    # Return the tuples list
    return tuples

def get_word_properties_from_azure_json(json_object) -> list[dict]:
    """
    Get the word properties from the azure json object
    It also calculate the height of the word box
    :param json_object:
    :return:
    """
    word_boxes = []
    for result in json_object['analyzeResult']['readResults']:
        for line in result['lines']:
            if 'boundingBox' in line and 'text' in line:
                if 'words' in line:
                    cluster_detail = {
                            "word_cluster":None,
                            "word_cluster_box":None,
                            "words":[]
                        }
                    cluster_detail['word_cluster'] = line['text']
                    cluster_detail['word_cluster_box'] = convert_to_xy_tuple(line['boundingBox'])
                    for word in line['words']:
                        if 'boundingBox' in word and 'text' in word:
                            # logger.debug("WR: %s S: %s", ratio, word['boundingBox'])
                            word['boundingBox'] = convert_to_xy_tuple(word['boundingBox'])
                            # logger.debug(" -> %s", cluster_detail['word_cluster_box'])
                            cluster_detail['words'].append(word)

                    # logger.debug("CR: %s S: %s -> %s", ratio, line['boundingBox'], cluster_detail['word_cluster_box'])
                    word_boxes.append(cluster_detail)
    return word_boxes


def draw_text_boxes_on_img(image: np.ndarray, word_properties: list[dict]):
    """
    Draw text boxes on an image from OCR results.

    This function takes in an image and word properties from OCR results, 
    and draws the bounding boxes and text onto the image.

    Parameters
    -------
    - `image` (np.ndarray): The input image
    - `word_properties` (list of dicts): A list of dictionaries containing 
        word properties like bounding boxes and text from the OCR results

    Returns
    -------
        np.ndarray: The image with text boxes drawn on it
    """
    markup_image = image.copy() # <TODO> change it to cope with different image formats
    if markup_image is not None:
        ploylines = [word['boundingBox'] for d in word_properties for word in d['words']] # select all bounding boxes
        text_list = [word['text'] for d in word_properties for word in d['words']] # select all texts
        contours = np.array(ploylines, dtype=np.int32)
        cv2.drawContours(image=markup_image, contours=contours, contourIdx=-1, color=(0,0,255), thickness=1) #  markup_image = draw_polygons(markup_image, contours, (0, 255, 0))

        for tidx, (text_val, contour) in enumerate(zip(text_list, contours)):
            M = cv2.moments(contour)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            cv2.putText(markup_image, str(tidx), org= (cx,cy), fontScale=1, color=(255, 0, 0), thickness=1, fontFace=cv2.FONT_HERSHEY_SIMPLEX)
            # logger.debug("Idx: %s Text: %s Contour: %s ", tidx, text_val, contour)

        # data['images']['markup'] = markup_image
    return markup_image

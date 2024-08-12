import os
import numpy as np
import openai
from openai.types.chat import ChatCompletion
from dotenv import load_dotenv
# from pprint import PrettyPrinter

load_dotenv()
# Set the API key, endpoint, and type for Azure, deployment name
openai.api_key = os.getenv('OPENAI_API_KEY') 
openai.azure_endpoint = os.getenv('OPENAI_AZURE_ENDPOINT') 
openai.api_type = os.getenv('OPENAI_API_TYPE')
openai.api_version = os.getenv('OPENAI_API_VERSION')
deployment_name = os.getenv('OPENAI_DEPLOYMENT_NAME')

def text_to_llm(output_data: str) -> ChatCompletion:
    """
    Send text into LLM (GPT4o)
    
    Returns:
    ChatCompletion: The response from OpenAI containing the extracted info
    """
   
    # Define the prompt
    prompt = [
        {"role":"system",
         "content":"""
                I have done OCR and got the results as below. Please give me the tag number and manufacturer. 
                Return the values without explanation.
            """
            },
        # {"role":"user",
        #  "content":"""[{
        #             "Dept" : "DEPT.  ENG",
        #             "Linenum" : "LINE NO.  11-0 - 1165-2-UBI",
        #             "Title" : "TITLE RELIEF FROM PSVILOIA TO FLARE  HEADER (FILTER LILO1A)",
        #             "Drawnum" : "DWG. NO.  11-0-1165-BT",
        #             "Revnum" : "REV.  O"
        #     }]"""},
        # {"role":"assistant",
        #  "content":"""[{
        #             "Dept" : "ENG",
        #             "Linenum" : "11-0-1165-2-UBI",
        #             "Title" : "RELIEF FROM PSVILOIA TO FLARE HEADER (FILTER LILOIA)",
        #             "Drawnum" : "11-0-1165-BT",
        #             "Revnum" : "0"
        #     }]"""},
        {"role":"user",
         "content": output_data}
        ]

    # pp = PrettyPrinter(indent=4)
    # logger.info("Prompt: %s", pp.pformat(prompt))
    response = openai.chat.completions.create(
        model=deployment_name,
        temperature=0,
        messages=prompt,
    )
    # logger.info("Prompt tokens: %s, Completion tokens: %s, Total tokens: %s", response.usage.prompt_tokens, response.usage.completion_tokens, response.usage.total_tokens)
    # Print the response from the API
    # print(response.choices[0].message.content) 
    return response



def img_to_llm(img:np.ndarray, question: str) -> ChatCompletion:
    """
    Send text into LLM (GPT4o)
    
    Returns:
    ChatCompletion: The response from OpenAI containing the extracted info
    """
   
    # Define the prompt
    prompt = [
        {"role":"system",
        "content": [
			{
				"type": "text",
				"text": "You are an AI assistant that helps people find information."
			}
		],
        },
        {"role":"user",
         "content": question #Please give me the tag number and manufacturer.  Return the values without explanation.
         }
        ]


    response = openai.chat.completions.create(
        model=deployment_name,
        temperature=0,
        messages=prompt,
    )
    # response from the API
    # print(response.choices[0].message.content) 
    return response

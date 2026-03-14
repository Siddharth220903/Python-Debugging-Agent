import logging
logger = logging.getLogger("DebuggingAgent.model_inference")

import json
from pathlib import Path

from google import genai
from google.genai import types

from .model_utils import get_api_key
from .model_utils import check_json_format

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR/".env"

with open(BASE_DIR / 'model_details.json', 'r') as json_file: 
     model_details = json.load(json_file)

def initializeCheckerAPI() -> genai.client.Client: 
    """
    Initializes the Checker API using the Google Gemini.

    :return: Initialized genai.client.Client instance
    :rtype: genai.client.Client
    """

    logger.info("Initializing checker API from Gemini.")
    api_key = get_api_key("checker_model")
    try:
        api = genai.Client(api_key=api_key)

        logger.info("Checker API initialized successfully.")
    except Exception as e:
        logger.info(f"Failed to initialize Checker API: {e}")
        return None
    return api

def checkCorrection(api: genai.client.Client, code_snippet: str, changes: str)->bool:
    """
    Checks the correction and rates it on a scale of 0-10 with a reasoning
    
    :param api: The initialized genai.client.Client instance
    :type api: genai.client.Client
    :param code_snippet: Code snippet that needs correction
    :type code_snippet: str
    :param changes: Changes suggested by Inference Model 
    :type changes: str
    :return: Code correction in specified json format
    :rtype: str
    """
    if(check_json_format == False): 
        logger.info(f"Invalid format found. Retry the inference....")
        return False
    
    system_prompt = """

    """

    message = """

    """
    
    response = api.models.generate_content(
        model=model_details["checker_model_name"], 
        config=types.GenerateContentConfig(
            system_instruction=system_prompt
        ), 
        contents=message
    )
    return True
    



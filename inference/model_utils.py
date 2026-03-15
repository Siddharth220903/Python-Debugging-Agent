import logging
logger = logging.getLogger("DebuggingAgent.model_inference")

from dotenv import load_dotenv, set_key
import os
import json
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR/".env"

with open(BASE_DIR / 'model_details.json', 'r') as json_file: 
     model_details = json.load(json_file)

def get_api_key(key: str):

    load_dotenv(dotenv_path=ENV_FILE)
    API_KEY = os.getenv(key)
    if not API_KEY:
        logger.info("No API Key found.")
        GENERATE_URL = model_details[f"{key}_webpage"]
        choice = input("Want to create a new API Key? Enter 'y' or 'n': ")
        if choice == 'y':
              logger.info("Opening Browser...")
              webbrowser.open(GENERATE_URL)
        API_KEY = input("\nPaste your key here: ")
        
        ENV_FILE.touch(exist_ok=True)
        set_key(str(ENV_FILE), key,API_KEY)
        logger.info("Key saved successfully.")
    return API_KEY


def check_json_format(changes: str) -> bool:
    """
    Checks if the provided JSON string has the correct structure for code changes.
    
    The expected structure is a JSON object with:
    - "Line": integer
    - "Tag": string, one of ["deleted", "modified", "created"]
    - "Change": string
    
    :param changes: JSON string to validate
    :type changes: str
    :return: True if the structure is valid, False otherwise
    :rtype: bool
    """
    try:
        data = json.loads(changes)
    except json.JSONDecodeError:
        return False
    
    if not isinstance(data, dict):
        return False
    
    required_keys = {"Line", "Tag", "Change"}
    if set(data.keys()) != required_keys:
        return False
    
    if not isinstance(data["Line"], int):
        return False
    
    if not isinstance(data["Tag"], str) or data["Tag"] not in ["deleted", "modified", "created"]:
        return False
    
    if not isinstance(data["Change"], str):
        return False
    
    return True

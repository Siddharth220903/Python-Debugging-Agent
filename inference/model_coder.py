import logging
logger = logging.getLogger("DebuggingAgent.model_inference")

from dotenv import load_dotenv, set_key
from huggingface_hub import InferenceClient
import os
import json
import webbrowser
from pathlib import Path

from .model_inference import get_api_key, initializeInferenceAPI

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR/".env"

with open(BASE_DIR / 'model_details.json', 'r') as json_file: 
     model_details = json.load(json_file)

def initializeCoderAPI()->InferenceClient: 
    """
    Initializes the Inference API using the Huggingface Hub.

    :return: Initialized InferenceClient instance
    :rtype: InferenceClient
    """

    logger.info("Initializing coder API from HF.")
    api_key = get_api_key()

    try:
        api = InferenceClient(
            model=model_details["model_name"], 
            token=api_key
        )

        logger.info("Coder API initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Coder API: {e}")
        raise Exception(f"Failed to initialize coder API. Please check your HF_API_KEY and internet connection.")
    return api

def _check_json_format(changes: str) -> bool:
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

def createCode(api: InferenceClient, code_snippet: str, changes : str) -> str: 
    """
    Gets the complete corrected code from the Coder API based on the provided code snippet and changes suggested by the inference model.
    
    :param api: The initialized InferenceClient instance
    :type api: InferenceClient
    :param code_snippet: Code snippet that needs correction
    :type code_snippet: str
    :param changes: Changes suggested by Inference Model 
    :type changes: str
    :return: Code correction in specified json format
    :rtype: str
    """
    if(_check_json_format == False): 
        logger.info(f"Invalid format found. Retry the inference....")
        return code_snippet
    
    messages = [
        {
            "role" : "system", 
            "content" : (
                """
                    You are an expert Python 3.11 developer. Your task is to apply a set of structured changes to an original source code file to produce a final, error-free version.

                    You will receive:
                    1. The Original Source Code.
                    2. A JSON object containing a list of "changes" with keys: "Line" (integer), "Tag" ("modified", "deleted", "created"), and "Change" (string).

                    Your instructions:
                    - Reconstruct the entire Python file by applying the specified changes to the original lines.
                    - For "modified": Replace the code at the specified Line number with the "Change" string.
                    - For "deleted": Remove the specified Line number entirely.
                    - For "created": Insert the "Change" string as a new line immediately following the specified Line number.
                    - Maintain all original indentation and whitespace for lines not mentioned in the JSON.
                    - Ensure the final output is valid Python 3.11 code.

                    Return your response STRICTLY as a JSON object with a single key "fixed_code". The value must be the complete, reconstructed Python code as a single string. 

                    Do not include explanations, markdown blocks, or any text outside the JSON structure.

                    Example Output Format:
                    {
                    "fixed_code": "import os\n\ndef main():\n    print('Fixed!')\n\nif __name__ == '__main__':\n    main()"
                    }
                """
            )
        }, 
        {
            "role" : "user", 
            "content" : (
                f"--- CHANGES ---\n{changes}\n\n"
                f"--- ORIGINAL CODE ---\n{code_snippet}\n\n"
            ) 
        }
    ]

    response_format = {
        "type": "json_object",
        "schema": {
            "type": "object",
            "properties": {
                "fixed_code": { "type": "string" }
            },
            "required": ["fixed_code"]
        }
    }


    response = api.chat_completion(
        messages = messages,
        max_tokens=model_details["max_output_token"],
        response_format={
            "type": "json_object",
            "value": response_format
        }, 
        stream=False
    )

    logger.info("Received corrected code from Coder API.")

    try:
        json.loads(response.choices[0].message.content)
        logger.info("Valid JSON format obtained.")
    except json.JSONDecodeError:
            logger.info("Invalid JSON format from model.")
            raise Exception(f"Invalid JSON format from model.")

    
    return response.choices[0].message.content


import logging
logger = logging.getLogger("DebuggingAgent.model_inference")

from dotenv import load_dotenv, set_key
from huggingface_hub import InferenceClient
import os
import json
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR/".env"

tool = None

import retriever

with open(BASE_DIR / 'model_details.json', 'r') as json_file: 
     model_details = json.load(json_file)

def get_api_key():

    load_dotenv(dotenv_path=ENV_FILE)
    HF_API_KEY = os.getenv("HF_API_KEY")
    if not HF_API_KEY:
        logger.info("No API Key found.")
        GENERATE_URL = "https://huggingface.co/docs/huggingface_hub/v0.5.1/en/package_reference/hf_api"
        choice = input("Want to create a new API Key? Enter 'y' or 'n': ")
        if choice == 'y':
              logger.info("Opening Browser...")
              webbrowser.open(GENERATE_URL)
        HF_API_KEY = input("\nPaste your key here: ")
        
        ENV_FILE.touch(exist_ok=True)
        set_key(str(ENV_FILE), "HF_API_KEY", HF_API_KEY)
        logger.info("Key saved successfully.")
    return HF_API_KEY

def initializeInferenceAPI() -> InferenceClient:
    """
    Initializes the Inference API using the Huggingface Hub.

    :return: Initialized InferenceClient instance
    :rtype: InferenceClient
    """

    logger.info("Initializing inference API from HF.")
    api_key = get_api_key()
    try:
        api = InferenceClient(
            model=model_details["model_name"], 
            token=api_key
        )

        logger.info("Inference API initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Inference API: {e}")
        raise Exception(f"Failed to initialize Inference API. Please check your HF_API_KEY and internet connection.")
    return api

def getCodeCorrection(api: InferenceClient, code_snippet: str, error_message: str) -> str:

    """
    Gets the code correction from the Inference API based on the provided code snippet and error message.
    
    :param api: The initialized InferenceClient instance
    :type api: InferenceClient
    :param code_snippet: Code snippet that needs correction
    :type code_snippet: str
    :param error_message: Error message encountered during code execution
    :type error_message: str
    :return: Corrected code snippet in json format
    :rtype: str
    """
    global tool 

    if tool is None:
        logger.info("Initializing Retrieval Tool.")
        tool = retriever.RetrievalTool()

    try: 
        retrieved_docs = tool.retrieve(terminal_error=error_message)
        logger.info("Successfully retrieved source.")
    except retriever.NoDocumentError:
         retrieved_docs = ""
         logger.info("No Relevant Data Found.")

    messages = [
        {
            "role": "system", 
            "content": (
               """
                You are an expert Python 3.11 developer. Your task is to analyze the provided code and Documentation Resources to fix errors. 
                You must retain the original logic of the code. 
                Return your response STRICTLY as a JSON object containing a three keys "Line", "Tag", and "Change". Each object must follow this schema:

                1. "Line": The integer line number in the original code where the change occurs.
                2. "Tag": Must be exactly one of: "deleted", "modified", or "created". 
                - Use "created" to insert a new line AFTER the specified line number.
                3. "Change": The actual Python code for the new or modified line. For "deleted", provide an empty string.

                Prioritize usage examples from the Documentation Resources. Do not include explanations, markdown blocks, or any text outside the JSON structure.

                Example Output Format:
                
                    {
                    "Line": 12,
                    "Tag": "modified",
                    "Change": "    return x + y"
                    },
                    {
                    "Line": 5,
                    "Tag": "deleted",
                    "Change": ""
                    }
                
                """
            )
        },
        {
            "role": "user", 
            "content": (
                f"--- DOCUMENTATION RESOURCES ---\n{retrieved_docs}\n\n"
                f"--- ORIGINAL CODE ---\n{code_snippet}\n\n"
                f"--- TERMINAL ERROR ---\n{error_message}"
            )
        }
    ]

    response_format = {
        "type": "json_object",
        "schema": {
            "type": "object",
            "properties": {
                "Line": { "type": "integer" },
                "Tag": { 
                    "type": "string", 
                    "enum": ["deleted", "modified", "created"] 
                },
                "Change": { "type": "string" }
            },
            "required": ["Line", "Tag", "Change"]
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

    logger.info("Received code correction from inference API.")

    try:
        json.loads(response.choices[0].message.content)
        logger.info("Valid JSON format obtained.")
    except json.JSONDecodeError:
            logger.info("Invalid JSON format from model.")
            raise Exception(f"Invalid JSON format from model.")

    
    return response.choices[0].message.content



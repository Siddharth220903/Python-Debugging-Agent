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

import retriever

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
    api = get_api_key()
    try:
        api = InferenceClient(
            model="meta-llama/Llama-3.1-8B-Instruct", 
            token=api
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
                "You are an expert Python developer specialized in Python 3.11. "
                "Your task is to fix the provided code error using the provided Documentation Resources. "
                "If the Documentation Resources contain specific usage examples or rules, prioritize them. "
                "Return the response STRICTLY as a JSON object with a single key 'fixed_code'. "
                "The value must be the complete, corrected Python code as a string. "
                "Do not include explanations, markdown blocks, or any text outside the JSON structure."
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
    response = api.chat_completion(
        messages = messages,
        max_tokens=1500
    )
    logger.info("Received code correction from inference API.")

    try:
        json.loads(response.choices[0].message.content)
        logger.info("Valid JSON format obtained.")
    except json.JSONDecodeError:
            raise Exception(f"Invalid JSON format from model.")

    
    return response.choices[0].message.content



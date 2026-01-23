from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import os
import json
import logging
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from retriever import retriever
logger = logging.getLogger(__name__)

env_path = "./.env"
load_dotenv(dotenv_path=env_path)
HF_API_KEY = os.getenv("HF_API_KEY")


def initializeInferenceAPI() -> InferenceClient:
    """
    Initializes the Inference API using the Huggingface Hub.

    :return: The initialized InferenceClient instance
    :rtype: InferenceClient
    """

    logger.info("Initializing inference API with huggingface hub.")
    try:
        api = InferenceClient(model="meta-llama/Llama-3.1-8B-Instruct", token=HF_API_KEY)
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
        print("Found relevant resources from documentation.")
        logger.info("Successfully Retrieved source.")
    except retriever.NoDocumentError:
         retrieved_docs = ""
         print("No relevant document found.")
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



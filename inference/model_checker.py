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
    if(check_json_format(changes) == False): 
        logger.info(f"Invalid format found. Retry the inference....")
        return False
    
    system_prompt = """
            ### Role
            You are an expert Python Code Auditor. 
            Your task is to evaluate a proposed modification to a provided Python code snippet and assign a quality score based on its impact.

            ### Input Format
            The user will provide two inputs:
            1. "Original Code": The base Python script.
            2. "Modification": A JSON object containing:
                - "Line": The integer line number targeted.
                - "Tag": One of ["deleted", "modified", "created"].
                - "Change": The string content of the code change.

            ### Evaluation Criteria
            Assign a "score" from 0 to 10 based on:
            - Accuracy: Does the change correctly address a bug or logic error?
            - Efficiency: Does it improve or maintain performance?
            - Style: Does it follow PEP 8 and Pythonic idioms?
            - Safety: Does it introduce security vulnerabilities or breaking changes?

            ### Output Format
            You must return a valid JSON object only. Do not include markdown formatting or conversational text. The JSON must follow this schema:
            {
            "score": number, // 0 to 10 (can be float or integer)
            "reason": "string" // A concise explanation for the score assigned.
            }
    """

    message = f"""
        "Original Code" : {code_snippet}, 
        "Modification" : {changes}
    """
    
    response = api.models.generate_content(
        model=model_details["checker_model_name"], 
        config=types.GenerateContentConfig(
            system_instruction=system_prompt
        ), 
        contents=message
    )

    if(response.text is None):
        return True
    else: 
        review = json.loads(response.text)
        logger.info(
            "Score: {score}, Reasons: {reason}".format(score=review["score"], reason=review["reason"])
        )
    if((review["score"] is None) or  (review["score"] >= model_details["checker_threshold"])): 
        logger.info("Code changes confirmed...")
        return True 
    else:
        return False    



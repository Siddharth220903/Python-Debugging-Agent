import logging
logger = logging.getLogger("DebuggingAgent.model_inference")

import json

from google import genai
from google.genai import types

from .llm_model import LLMModel


class EvaluatorModel(LLMModel):

    def __init__(self, code_snippet:str):
        super().__init__(code_snippet=code_snippet)
        self._initializeAPI()


    def _initializeAPI(self) -> genai.client.Client: 
        """
        Initializes the Checker API using the Google Gemini.

        :return: Initialized genai.client.Client instance
        :rtype: genai.client.Client
        """

        logger.info("Initializing checker API from Gemini.")
        try:
            self.api = genai.Client(api_key=self._get_api_key("evaluator_model"))

            logger.info("Checker API initialized successfully.")
        except Exception as e:
            logger.info(f"Failed to initialize Checker API: {e}")
        
    def _systemPrompt(self):
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
        return system_prompt

    def modelInference(self, changes: str)->bool:
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
        if(self.check_json_format(changes) == False): 
            logger.info(f"Invalid format found. Retry the inference....")
            return False
        

        message = f"""
            "Original Code" : {self.code_snippet}, 
            "Modification" : {changes}
        """
        
        response = self.api.models.generate_content(
            model=self.model_details["evaluator_model_name"], 
            config=types.GenerateContentConfig(
                system_instruction=self._systemPrompt()
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
        if((review["score"] is None) or  (review["score"] >= self.model_details["evaluator_threshold"])): 
            logger.info("Code changes confirmed...")
            return True 
        else:
            return False    



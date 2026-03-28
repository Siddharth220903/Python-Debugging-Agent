import logging
logger = logging.getLogger("DebuggingAgent.model_inference")

from huggingface_hub import InferenceClient
import json
from pathlib import Path
from rag_retriever.retriever_tool import RetrievalTool
from rag_retriever.retriever_tool import NoDocumentError
from .llm_model import LLMModel

class InferenceModel(LLMModel): 
    def __init__(self, code_snippet : str):
        super().__init__(code_snippet=code_snippet)
        self.retreiver_tool = None
        self.api = self._initializeAPI()

    def _initializeAPI(self) -> InferenceClient:
        """
        Initializes the Inference API using the Huggingface Hub.

        :return: Initialized InferenceClient instance
        :rtype: InferenceClient
        """

        logger.info("Initializing inference API from HF.")
        try:
            api = InferenceClient(
                model=self.model_details["model_name"], 
                token=self._get_api_key("model")
            )

            logger.info("Inference API initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Inference API: {e}")
            raise Exception(f"Failed to initialize Inference API. Please check your model and internet connection.")
        return api

    def _systemPrompt(self):
        system_prompt = """
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
        return system_prompt
    
    def modelInference(self, error_message: str) -> str:

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

        if self.retreiver_tool is None:
            logger.info("Initializing Retrieval Tool.")
            self.retreiver_tool = RetrievalTool()

        try: 
            retrieved_docs = self.retreiver_tool.retrieve(terminal_error=error_message)
            logger.info("Successfully retrieved source.")
        except NoDocumentError:
            retrieved_docs = ""
            logger.info("No Relevant Data Found.")

        messages = [
            {
                "role": "system", 
                "content": (self._systemPrompt())
            },
            {
                "role": "user", 
                "content": (
                    f"--- DOCUMENTATION RESOURCES ---\n{retrieved_docs}\n\n"
                    f"--- ORIGINAL CODE ---\n{self.code_snippet}\n\n"
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
        
        response = self.api.chat_completion(
            messages = messages,
            max_tokens=self.model_details["max_output_token"],
            response_format={
                "type": "json_object",
                "value": response_format
            }, 
            stream=False
        )

        logger.info("Received code correction from inference API.")

        if(self.check_json_format(response.choices[0].message.content)):
            logger.info("Valid JSON format obtained.")
        else:
            logger.info("Invalid JSON format from model.")
            return None

        
        return response.choices[0].message.content



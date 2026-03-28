
import logging
logger = logging.getLogger("DebuggingAgent.file_handler")

import json
from urllib import response

class FileHandler():

    def __init__(self, file_path:str): 
        self.file_path = file_path

    def readPythonFile(self) -> str:
        """
        Reads and returns the content of a Python file as a string.

        :param file_path: Path to the Python file.
        :type file_path: str
        :return: Content of the file as a string.
        :rtype: str
        """
        logger.info("Attempting to reading python code.")
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                code_string = file.read()
                logger.info(f"Successfully read code from {self.file_path}")
                return code_string
        except Exception as e:
            logger.error(f"An error occurred while reading the file: {e}")
            raise Exception(f"Could not read file {self.file_path}. Check the file path and permissions.") 



    def writeCodeToFile(self, code_snippet: str):

        """
        Wrties the corrected code snippet to the specified file.
        
        :param file_path: File path where the code needs to be written
        :type file_path: str
        :param code_snippet: Corrected code snippet in JSON format
        :type code_snippet: str
        """

        try:
            data = json.loads(code_snippet)
            fixed_code = data.get("fixed_code", "")
            with open(self.file_path, 'w') as f:
                f.write(fixed_code)

            logger.info(f"Successfully wrote code to {self.file_path}.")
            
        except Exception as e:
            logger.error(f"Failed to write code to {self.file_path}.")
            raise Exception(f"Failed to write code to {self.file_path}. Check the file path and permissions.")
import logging
import json
from urllib import response
logger = logging.getLogger(__name__)

def write_code_to_file(file_path: str, code_snippet: str):

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
        with open(file_path, 'w') as f:
            f.write(fixed_code)

        logger.info(f"Successfully wrote code to {file_path}.")
        
    except Exception as e:
        logger.error(f"Failed to write code to {file_path}.")
        raise Exception(f"Failed to write code to {file_path}. Check the file path and permissions.")
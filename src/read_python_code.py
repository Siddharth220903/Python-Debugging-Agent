
import logging
logger = logging.getLogger(__name__)

def read_python_file(file_path):
    """
    Reads and returns the content of a Python file as a string.
    :param file_path: Path to the Python file.
    :return: Content of the file as a string.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            code_string = file.read()
            logger.info(f"Successfully read code from {file_path}")
            return code_string
    except Exception as e:
        logger.error(f"An error occurred while reading the file: {e}")
        raise Exception(f"Could not read file {file_path}. Check the file path and permissions.") 
    
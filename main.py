import argparse
from pathlib import Path
import logging

BASE_DIR = Path(__file__).resolve().parent

import logger_setup
logger = logger_setup.setup_logger("DebuggingAgent")

import inference

if __name__ == "__main__":

    """
    Main function to debug a Python file using an AI model.
    """
    logger = logging.getLogger("DebuggingAgent")
    logger.info("We currently support only execution errors in a python file. Starting the application...")
    
    parser = argparse.ArgumentParser(description="Read from command line argument.")
    parser.add_argument('--file', type=str, help='The path to the file you want to read', required=True)
    parser.add_argument('--max_attempts', type=int, help='Maximum number of attempts to debug the code', default=3)
    args = parser.parse_args()
    file_path = args.file
    max_attempts = args.max_attempts
    logger.info(f"Read the parameters:\nFile Path: {file_path}\nMaximum Attempt: {max_attempts}")


    model_api = inference.initializeInferenceAPI()
    logger.info("Initialized Inference API")

    for attempt in range(max_attempts):
        logger.info(f"Attempt {attempt + 1} of {max_attempts}.")
        output, success = inference.executePythonFile(file_path)
        logger.info(f"Completed execution.")
        if success:
            logger.info("Code executed without execution errors.")
            break
        else:
            code_snippet = inference.read_python_file(file_path)
            logger.info("Successfully read code.")

            correction = inference.getCodeCorrection(
                api=model_api, 
                code_snippet=code_snippet, 
                error_message=output
            )
            logger.info("Corrected code received from model.")
            
            inference.write_code_to_file(file_path, correction)
            logger.info("Code written to file.")

    if not success:
        logger.error("Maximum attempts reached. Code could not be fixed.")
    else:
        logger.info("Debugging process completed successfully.")
    
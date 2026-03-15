import argparse
from pathlib import Path
import logging
import inference


BASE_DIR = Path(__file__).resolve().parent

import logger_setup
logger = logger_setup.setup_logger("DebuggingAgent")


if __name__ == "__main__":

    """
    Main function to debug a Python file using an AI model.
    """
    logger = logging.getLogger("DebuggingAgent")
    logger.info("We currently support only execution errors in a python file. Starting the application...")
    
    parser = argparse.ArgumentParser(description="Read from command line argument.")
    parser.add_argument('--file', type=str, help='The path to the file you want to read', default="test/sample.py")
    parser.add_argument('--max_attempts', type=int, help='Maximum number of attempts to debug the code', default=3)
    args = parser.parse_args()
    file_path = args.file
    max_attempts = args.max_attempts
    logger.info(f"Read the parameters:\nFile Path: {file_path}\nMaximum Attempt: {max_attempts}")


    model_api_infer = None 
    model_api_checker = None 
    model_api_coder = None
    

    for attempt in range(max_attempts):
        logger.info(f"Attempt {attempt + 1} of {max_attempts}.")
        output, success = inference.executePythonFile(file_path)
        logger.info(f"Completed execution.")
        if success:
            logger.info("Code executed without execution errors.")
            break
        else:
            if model_api_infer is None: 
                model_api_infer = inference.initializeInferenceAPI()
                logger.info("Initialized Inference API")
            
            if model_api_checker is None: 
                model_api_checker = inference.initializeCheckerAPI()
                logger.info("Initialized Checker API")

            if model_api_coder is None: 
                model_api_coder = inference.initializeCoderAPI()
                logger.info("Initialized Coder API")
            
            code_snippet = inference.read_python_file(file_path)
            logger.info("Successfully read code.")

            correction = inference.getCodeCorrection(
                api=model_api_infer, 
                code_snippet=code_snippet, 
                error_message=output
            )
            if correction is None: 
                logger.info("Invalid Inference Obtained. Try again...")
                continue
            logger.info("Correction received from model.")
            logger.info(f"Correction Received: {correction}")

            # Check without error log to avoid bias
            if model_api_checker is not None: 
                checkInfo = inference.checkCorrection(
                    api=model_api_checker, 
                    code_snippet=code_snippet, 
                    changes=correction
                )
                logger.info("Result received from checker model.")
                # Failed to pass check
                if not checkInfo:
                    logger.info("Inference result doesn't seem great. Trying further attempts...")
                    continue
                    

            corrected_code = inference.createCode(
                api=model_api_coder, 
                code_snippet=code_snippet, 
                changes=correction
            )

            logger.info(corrected_code)
            
            inference.write_code_to_file(file_path, corrected_code)
            logger.info("Code written to file.")

    output, success = inference.executePythonFile(file_path)

    if not success:
        logger.error("Maximum attempts reached. Code could not be fixed.")
    else:
        logger.info("Debugging process completed successfully.")
    
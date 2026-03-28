import argparse
from pathlib import Path
import logging

import logger_setup
logger = logger_setup.setup_logger("DebuggingAgent")

from inference_models.inference_model import InferenceModel
from inference_models.evaluator_model import EvaluatorModel
from inference_models.coder_model import CoderModel
from file_handler.file_handler import FileHandler 
from code_executor.code_executor import CodeExecutor

if __name__ == "__main__":

    """
    Main function to debug a Python file using an AI model.
    """
    BASE_DIR = Path(__file__).resolve().parent
    logger = logging.getLogger("DebuggingAgent")
    logger.info("We currently support only execution errors in a python file. Starting the application...")
    
    parser = argparse.ArgumentParser(description="Read from command line argument.")
    parser.add_argument('--file', type=str, help='The path to the file you want to read', default="test/sample.py")
    parser.add_argument('--max_attempts', type=int, help='Maximum number of attempts to debug the code', default=3)
    args = parser.parse_args()
    file_path = args.file
    max_attempts = args.max_attempts
    logger.info(f"Read the parameters:\nFile Path: {file_path}\nMaximum Attempt: {max_attempts}")

    file_handler = FileHandler(file_path=file_path)
    code_executor = CodeExecutor(file_path=file_path)

    inference_model = None 
    evaluator_model = None 
    coder_model = None

    for attempt in range(max_attempts):
        logger.info(f"Attempt {attempt + 1} of {max_attempts}.")
        output, success = code_executor.executePythonFile()
        logger.info(f"Completed execution.")
        if success:
            logger.info("Code executed without execution errors.")
            break
        else: 

            logger.info("Code Execution failed.")

            code_snippet = file_handler.readPythonFile()
            logger.info("Successfully read code.")

            if inference_model is None:
                inference_model = InferenceModel(code_snippet=code_snippet)
                logger.info("Initialized Inference API")
            
            if evaluator_model is None: 
                evaluator_model = EvaluatorModel(code_snippet=code_snippet)
                logger.info("Initialized Checker API")

            if coder_model is None:
                coder_model = CoderModel(code_snippet=code_snippet)
                logger.info("Initialized Coder API")
            
            correction = inference_model.modelInference(
                error_message=output
            )
            if correction is None: 
                logger.info("Invalid Inference Obtained. Try again...")
                continue
            logger.info("Correction received from model.")
            logger.info(f"Correction Received: {correction}")

            # Check without error log to avoid bias
            if evaluator_model is not None: 
                checkInfo = evaluator_model.modelInference(
                    changes=correction
                )
                logger.info("Result received from checker model.")
                # Failed to pass check
                if not checkInfo:
                    logger.info("Inference result doesn't seem great. Trying further attempts...")
                    continue
                    

            corrected_code = coder_model.modelInference(
                changes=correction
            )

            logger.info(corrected_code)
            
            file_handler.writeCodeToFile(corrected_code)
            logger.info("Code written to file.")

    output, success = code_executor.executePythonFile()

    if not success:
        logger.error("Maximum attempts reached. Code could not be fixed.")
    else:
        logger.info("Debugging process completed successfully.")
    
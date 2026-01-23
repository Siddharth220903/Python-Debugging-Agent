import argparse
import logging 
import os
from pathlib import Path

script_dir = Path(__file__).parent
logger = logging.getLogger(__name__)

import executor
import model_inferece
import read_python_code
import write_python_code

if __name__ == "__main__":

    """Main function to debug a Python file using an AI model."""

    parser = argparse.ArgumentParser(description="Read from command line argument.")
    parser.add_argument('--file', type=str, help='The path to the file you want to read', required=True)
    parser.add_argument('--max_attempts', type=int, help='Maximum number of attempts to debug the code', default=3)
    args = parser.parse_args()
    file_path = args.file
    max_attempts = args.max_attempts

    logging.basicConfig(filename=f'{script_dir}/log/logging.log', filemode='w', level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    if not os.path.isfile(file_path):
        logger.error(f"Invalid file path: {file_path}")
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")

    logger.info("Initializing Inference API")
    model_api = model_inferece.initializeInferenceAPI()

    for attempt in range(max_attempts):
        print(f"Attempt {attempt + 1} of {max_attempts}.")
        logger.info(f"Attempt {attempt + 1} of {max_attempts}.")
        logger.info("Starting execution")
        output, success = executor.executePythonFile(file_path)

        if success:
            print("Code Execution success")
            logger.info("Code executed successfully without errors.")
            break
        else:
            print("Code Excution Failed. Trying to get inference from LLM.")
            logger.info("Reading the erroneous code from file")
            code_snippet = read_python_code.read_python_file(file_path)

            logger.info("Sending prompt to get code correction")
            correction = model_inferece.getCodeCorrection(
                api=model_api, 
                code_snippet=code_snippet, 
                error_message=output
            )
            
            logger.info("Writing corrected code back to file")
            write_python_code.write_code_to_file(file_path, correction)
    if not success:
        logger.error("Maximum attempts reached. Code could not be fixed.")
        raise Exception("Maximum attempts reached. Code could not be fixed.")
    else:
        logger.info("Debugging process completed successfully.")
    
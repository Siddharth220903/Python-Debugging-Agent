import logging
logger = logging.getLogger("DebuggingAgent.executor")

import subprocess 
import os

def executePythonFile(file_path: str) -> tuple[str, bool]:
    """
    Executes a python file in your local system and returns the output or error message.

    :param file_path: Path to the Python file to execute
    :type file_path: str
    :return: A tuple containing the output string and a boolean indicating successful execution
    :rtype: tuple[str, bool]
    """

    current_os = os.name
    command = f"python {file_path}"
    if(current_os == 'nt'):
        logger.info("Executing given file on new terminal in Windows OS")
        outputString = ""
        success = False
        try:
            result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            check=True)
            outputString, success = result.stdout, True
        except subprocess.CalledProcessError as e:
            outputString, success = e.stderr, False
        logger.info("Execution of given file completed. Got: %s", outputString)    
        return outputString, success
    else: 
        error_msg = f"The current OS '{current_os}' is not supported yet."
        logger.error(error_msg)
        raise NotImplementedError(error_msg)

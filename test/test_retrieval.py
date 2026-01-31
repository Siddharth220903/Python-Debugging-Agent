import pytest
import os
from unittest.mock import patch
from inference import initializeInferenceAPI

def test_retrieval_tool_initialization():
    from retriever import RetrievalTool
    tool_instance = RetrievalTool() 
    assert isinstance(tool_instance, RetrievalTool)

@patch('inference.model_inference.get_api_key')
def test_initialize_api_with_mock(mock_get_key):
    mock_get_key.return_value = "hf_fake_token_12345"
    api = initializeInferenceAPI()
    assert api is not None
    mock_get_key.assert_called_once()

@patch('inference.model_inference.get_api_key')
def test_initialize_api_throws_exception(mock_get_key):
    expected_msg = "Failed to initialize Inference API. Please check your HF_API_KEY and internet connection."
    mock_get_key.side_effect = Exception(expected_msg)
    
    with pytest.raises(Exception) as excinfo:
        initializeInferenceAPI()
    assert expected_msg in str(excinfo.value)
    mock_get_key.assert_called_once()
"""Tests for ollama_client.py"""
import pytest
from unittest.mock import Mock, patch
import json
from ollama_client import chat_llm, extract_final_response


class TestOllamaClient:
    """Test suite for Ollama client functionality."""
    
    def test_extract_final_response_deepseek_r1(self):
        """Test extracting final response from deepseek-r1 model with thinking tokens."""
        # Test case with thinking tokens
        content_with_thinking = """
        <think>
        This is the model thinking about the problem.
        Let me analyze the user's request...
        I need to provide a helpful response.
        </think>
        
        This is the final response that should be returned.
        """
        
        result = extract_final_response(content_with_thinking, "deepseek-r1:14b")
        assert result == "This is the final response that should be returned."
        
        # Test case without thinking tokens
        content_without_thinking = "This is a direct response without thinking."
        result = extract_final_response(content_without_thinking, "deepseek-r1:14b")
        assert result == "This is a direct response without thinking."
        
        # Test case with multiple thinking sections
        content_multiple_thinking = """
        <think>First thinking section</think>
        Some intermediate content
        <think>Second thinking section</think>
        Final response after all thinking.
        """
        
        result = extract_final_response(content_multiple_thinking, "deepseek-r1:14b")
        assert result == "Final response after all thinking."
    
    def test_extract_final_response_other_models(self):
        """Test that other models return content unchanged."""
        content = "Regular response from other model"
        
        result = extract_final_response(content, "llama2:7b")
        assert result == "Regular response from other model"
        
        result = extract_final_response(content, "mistral:7b")
        assert result == "Regular response from other model"
    
    def test_extract_final_response_edge_cases(self):
        """Test edge cases for response extraction."""
        # Empty content
        result = extract_final_response("", "deepseek-r1:14b")
        assert result == ""
        
        # Only thinking tokens, no final response
        content_only_thinking = "<think>Only thinking, no response</think>"
        result = extract_final_response(content_only_thinking, "deepseek-r1:14b")
        assert result == "Only thinking, no response"  # Fallback to original
        
        # Malformed thinking tokens
        content_malformed = "<think>Thinking without closing tag"
        result = extract_final_response(content_malformed, "deepseek-r1:14b")
        assert result == "<think>Thinking without closing tag"
    
    @patch('requests.post')
    def test_chat_llm_success(self, mock_post):
        """Test successful LLM chat interaction."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {
                "content": "This is a test response from the LLM."
            }
        }
        mock_post.return_value = mock_response
        
        # Test input
        messages = [
            {"role": "user", "content": "Hello, test message"}
        ]
        
        # Call function
        result = chat_llm(messages, model="deepseek-r1:14b")
        
        # Assertions
        assert isinstance(result, str)
        assert result == "This is a test response from the LLM."
        
        # Verify the request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "http://localhost:11434/api/chat"
        
        # Verify request payload structure
        payload = call_args[1]['json']
        assert payload['model'] == "deepseek-r1:14b"
        assert payload['messages'] == messages
        assert payload['stream'] is False
    
    @patch('requests.post')
    def test_chat_llm_with_thinking_tokens(self, mock_post):
        """Test LLM chat with deepseek-r1 thinking tokens."""
        # Mock response with thinking tokens
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {
                "content": "<think>Let me think about this...</think>\n\nThis is the actual response."
            }
        }
        mock_post.return_value = mock_response
        
        messages = [{"role": "user", "content": "Test with thinking"}]
        result = chat_llm(messages, model="deepseek-r1:14b")
        
        # Should return only the content after </think>
        assert result == "This is the actual response."
    
    @patch('requests.post')
    def test_chat_llm_timeout_handling(self, mock_post):
        """Test timeout handling in LLM chat."""
        # Mock timeout exception
        mock_post.side_effect = Exception("Connection timeout")
        
        messages = [{"role": "user", "content": "test"}]
        
        # Should handle exception gracefully
        with pytest.raises(Exception):
            chat_llm(messages)
    
    @patch('requests.post')
    def test_chat_llm_default_model(self, mock_post):
        """Test default model parameter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "response"}
        }
        mock_post.return_value = mock_response
        
        messages = [{"role": "user", "content": "test"}]
        chat_llm(messages)  # No model specified, should use default
        
        # Verify default model was used
        payload = mock_post.call_args[1]['json']
        assert payload['model'] == "deepseek-r1:14b"
    
    @patch('requests.post')
    def test_chat_llm_custom_model(self, mock_post):
        """Test custom model parameter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "response"}
        }
        mock_post.return_value = mock_response
        
        messages = [{"role": "user", "content": "test"}]
        result = chat_llm(messages, model="custom-model")
        
        # Verify custom model was used
        payload = mock_post.call_args[1]['json']
        assert payload['model'] == "custom-model" 
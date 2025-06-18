"""Ollama API client for LLM interactions."""
import requests
import time
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-r1:14b")


def extract_final_response(content: str, model: str) -> str:
    """
    Extract the final response from model output, handling thinking tokens.
    
    Args:
        content: Raw response content from the model
        model: Model name to determine parsing strategy
        
    Returns:
        Cleaned response content
    """
    # Handle deepseek-r1 models that generate thinking tokens
    if "deepseek-r1" in model.lower():
        # Look for the end of thinking tokens
        think_end = "</think>"
        if think_end in content:
            # Extract everything after the </think> token
            parts = content.split(think_end, 1)
            if len(parts) > 1:
                final_response = parts[1].strip()
                # Return the final response if it's not empty
                if final_response:
                    return final_response
            # Fallback: if no content after </think>, try to find content between last </think> and end
            # This handles cases where there might be multiple thinking sections
        
        # Additional fallback: try to find content after <think> tags
        think_start = "<think>"
        if think_start in content and think_end in content:
            # Find all thinking sections and get content after the last one
            sections = content.split(think_end)
            if len(sections) > 1:
                final_response = sections[-1].strip()
                if final_response:
                    return final_response
    
    # For other models or if no thinking tokens found, return original content
    return content.strip()


def chat_llm(messages: List[Dict[str, str]], model: str = DEFAULT_MODEL) -> str:
    """
    Send messages to Ollama LLM and return response.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        model: Model name to use (default: deepseek-r1:14b)
        
    Returns:
        String response from the LLM (cleaned of thinking tokens for deepseek-r1)
        
    Raises:
        Exception: If request fails after retries or timeout
    """
    url = f"{OLLAMA_BASE_URL}/api/chat"
    
    payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }
    
    # Exponential backoff configuration
    max_retries = 10
    base_delay = 1
    timeout = 240
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                raw_content = result.get("message", {}).get("content", "")
                
                # Extract final response, handling thinking tokens
                final_content = extract_final_response(raw_content, model)
                return final_content
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:  # Last attempt
                raise Exception(f"Failed to connect to Ollama after {max_retries} attempts: {str(e)}")
            
            # Exponential backoff
            delay = base_delay * (2 ** attempt)
            print(f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
            time.sleep(delay)
    
    raise Exception("Max retries exceeded")


def generate_persona_reaction(persona: str, product_description: str, model: str = DEFAULT_MODEL) -> str:
    """
    Generate a synthetic target-customer reaction for a given persona and product.
    
    Args:
        persona: Description of the target persona
        product_description: Description of the product/brand
        model: Model to use for generation
        
    Returns:
        Synthetic customer reaction as string (cleaned of thinking tokens)
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You are the persona described below. React authentically to the product/brand "
                "as if you were this person. Express your genuine thoughts, concerns, interests, "
                "and buying motivations. Keep your reaction concise but insightful (2-3 sentences)."
            )
        },
        {
            "role": "user",
            "content": f"""
I am: {persona}

About this product/brand: {product_description}

My reaction:
            """.strip()
        }
    ]
    
    return chat_llm(messages, model)


def test_ollama_connection() -> bool:
    """
    Test connection to Ollama server.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        test_messages = [{"role": "user", "content": "Hello, this is a connection test."}]
        response = chat_llm(test_messages)
        return len(response.strip()) > 0
    except Exception:
        return False 
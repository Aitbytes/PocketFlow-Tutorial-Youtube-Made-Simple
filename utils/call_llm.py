#import google.generativeai as genai
import os
from google import genai

def call_llm(prompt: str) -> str:
    """
    Call Google's Gemini LLM with a prompt and return the response.
    
    Args:
        prompt: The text prompt to send to the LLM
        
    Returns:
        str: The LLM's response text
        
    Raises:
        Exception: If the API call fails or the response is invalid
    """
    client = genai.Client()
    response = client.models.generate_content(
    model='gemini-2.5-flash-preview-05-20',
    contents=prompt
    )

    
    return response.text

if __name__ == "__main__":
    test_prompt = "Hello, how are you?"
    response = call_llm(test_prompt)
    print(f"Test successful. Response: {response}")

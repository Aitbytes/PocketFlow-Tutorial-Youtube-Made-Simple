from anthropic import Anthropic
import os

def call_llm(prompt: str) -> str:
    """
    Call Anthropic's Claude LLM with a prompt and return the response.
    
    Args:
        prompt: The text prompt to send to the LLM
        
    Returns:
        str: The LLM's response text
        
    Raises:
        Exception: If the API call fails or the response is invalid
    """
    client = Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    response = client.messages.create(
        max_tokens=1024,
        model="claude-3-sonnet-20240229",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

if __name__ == "__main__":
    test_prompt = "Hello, how are you?"
    response = call_llm(test_prompt)
    print(f"Test successful. Response: {response}")

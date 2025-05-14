from anthropic import AnthropicVertex
import os

def call_llm(prompt: str) -> str:
    client = AnthropicVertex(
        region=os.getenv("ANTHROPIC_REGION", "us-east5"),
        project_id=os.getenv("ANTHROPIC_PROJECT_ID", "")
    )
    response = client.messages.create(
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        model="claude-3-5-sonnet"
    )
    return response.content[0].text

if __name__ == "__main__":
if __name__ == "__main__":
    test_prompts = [
        "Hello, how are you?",
        "Explain what a Python decorator is in simple terms for a junior developer",
        "What are the key benefits of using Docker?"
    ]
    
    print("Testing LLM calls with multiple prompts...")
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\nTest {i}:")
        print(f"Prompt: {prompt}")
        try:
            response = call_llm(prompt)
            print(f"Response: {response[:200]}...")
            print("✓ Success")
        except Exception as e:
            print(f"✗ Error: {str(e)}")

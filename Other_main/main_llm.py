from apis.llm_api import LLMClient
from prompter import get_prompt

from dotenv import load_dotenv
import os
load_dotenv()

def main():
    # Replace with your NVIDIA API key

    # Initialize client
    llm = LLMClient(api_key=os.getenv("LLM_API_KEY"))

    # Example static query
    query = "Plan me a 1-day trip in Delhi covering Red Fort and India Gate."

    # Get prompt template and format with any necessary parameters
    base_prompt = get_prompt("qa", domain="travel planning")
    final_prompt = base_prompt + query

    response = llm.query(query)

    print("\nLLM Response:\n", response)

if __name__ == "__main__":
    main()

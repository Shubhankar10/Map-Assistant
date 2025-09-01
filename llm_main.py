from apis.llm_interface import LLMClient

def main():
    # Replace with your NVIDIA API key

    # Initialize client
    llm = LLMClient()

    # Example static query
    query = "Plan me a 1-day trip in Delhi covering Red Fort and India Gate."
    response = llm.query(query)

    print("\nLLM Response:\n", response)

if __name__ == "__main__":
    main()

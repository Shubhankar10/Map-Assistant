from apis.llm_api import LLMClient
from dotenv import load_dotenv  
import os
load_dotenv()

# Global variables to hold initialized clients
_llm_client = None
_api_client = None
_db_client = None


def initialize_services():
    global _llm_client, _api_client, _db_client

    print("[Initializer] Initializing all services...")

    # Initialize LLM
    #Jab bhi new LLM client use karna ho to ye line copy karna bas
    _llm_client = LLMClient(api_key=os.getenv("LLM_API_KEY"))
    print("[Initializer] LLMClient initialized.")

    # TODO: Initialize your API client(s)
    # TODO: Initialize your DB client

    print("[Initializer] All services initialized successfully.")


def ask_llm(query: str) -> str:
    
    global _llm_client
    if _llm_client is None:
        raise RuntimeError("LLMClient not initialized. Call initialize_services() first.")

    print("[Steps : ask_llm] Sending query to LLM...")
    response = _llm_client.query(query)
    print("[Steps : ask_llm] LLM response received.")
    return response



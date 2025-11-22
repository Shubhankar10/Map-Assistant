import json
def clean_llm_json(text: str) -> str:
    """
    Extracts the first valid JSON object or array from an LLM response.
    Automatically removes code fences and extra text.
    """

    import re

    # Remove markdown fences like ```json, ```js, ```text, or ```
    text = re.sub(r"```(\w+)?", "", text).strip()

    # Regex to capture the first {...} or [...]
    json_match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', text)

    if not json_match:
        raise ValueError("No JSON object or array found in LLM response.")

    return json_match.group(1).strip()

def print_json(text:str):
    print(json.dumps(text, indent=4))
    return
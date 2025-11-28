# # db_llm_executor.py
# import json
# import re 
# from typing import Dict, Any, List, Optional

# from steps import ask_llm
# from steps_new import clean_llm_json


# def _call_llm_raw(prompt: str) -> str:
#     """Thin wrapper so calls are easy to change later."""
#     return ask_llm(prompt)


# def _parse_json_from_llm_response(raw: str) -> Dict[str, Any]:
#     """
#     Try clean_llm_json then json.loads(raw).
#     Returns parsed object or raises ValueError.
#     """
#     try:
#         cleaned = clean_llm_json(raw)
#         return json.loads(cleaned)
#     except Exception:
#         try:
#             return json.loads(raw)
#         except Exception as e:
#             raise ValueError(f"Failed to parse LLM output as JSON: {e}\nRaw:\n{raw}")


# def analyze_with_llm(analyzer_prompt_obj: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     Call analyzer LLM with analyzer_prompt (produced by db_llm_builder).
#     Expect the LLM to return JSON containing at least a 'final_prompt' field.
#     Returns a dict containing:
#       { "task":..., "analyzer_raw":..., "analyzer_parsed": {...} }
#     """
#     prompt_text = analyzer_prompt_obj["analyzer_prompt"]
#     task = analyzer_prompt_obj.get("task")
#     raw = _call_llm_raw(prompt_text)
#     try:
#         parsed = _parse_json_from_llm_response(raw)
#     except ValueError as e:
#         return {"task": task, "analyzer_raw": raw, "error": str(e)}

#     if not isinstance(parsed, dict) or "final_prompt" not in parsed:
#         return {"task": task, "analyzer_raw": raw, "analyzer_parsed": parsed,
#                 "error": "analyzer output missing 'final_prompt' field"}

#     return {"task": task, "analyzer_raw": raw, "analyzer_parsed": parsed}


# def substitute_placeholders_with_json_arrays(final_prompt: str, placeholder_values: Dict[str, Any]) -> str:
#     """
#     Replace placeholders like <languages> with a JSON array literal, e.g. ["Telugu"].
#     Uses REGEX to be case-insensitive (handles <Languages>, <LANGUAGES>, etc).
#     """
#     out = final_prompt
#     for k, v in placeholder_values.items():
#         # 1. Clean the key: remove < and > if they exist to get the raw name
#         raw_key = k.replace("<", "").replace(">", "")
        
#         # 2. Create a pattern that matches <raw_key> case-insensitively
#         # re.escape ensures special characters in keys don't break regex
#         pattern = re.compile(f"<{re.escape(raw_key)}>", re.IGNORECASE)
        
#         # 3. Serialize the value to JSON
#         replacement = json.dumps(v, ensure_ascii=False)
        
#         # 4. Substitute
#         out = pattern.sub(replacement, out)
        
#     return out


# def filter_execution_result_to_requested(parsed, requested_values: List[str]):
#     """
#     Keep only items whose 'language' field matches requested_values (case-insensitive).
#     parsed may be a list of objects or a dict; returns a list filtered to requested_values.
#     """
#     if parsed is None:
#         return []

#     # Normalize requested set
#     req = {s.strip().lower() for s in requested_values}

#     # Normalize parsed into list of objects
#     parsed_list = []
#     if isinstance(parsed, dict):
#         # If dict maps language -> object, convert to list
#         for k, v in parsed.items():
#             if isinstance(v, dict):
#                 obj = dict(v)
#                 if "language" not in obj:
#                     obj["language"] = k
#                 parsed_list.append(obj)
#     elif isinstance(parsed, list):
#         parsed_list = parsed
#     else:
#         return []

#     filtered = [
#         item for item in parsed_list
#         if isinstance(item.get("language"), str) and item.get("language").strip().lower() in req
#     ]
#     return filtered


# def execute_final_prompt(final_prompt_text: str) -> Dict[str, Any]:
#     """
#     Call LLM with the substituted final prompt and parse JSON output.
#     Returns dict { "execution_raw": ..., "execution_parsed": ... } or error.
#     """
#     raw = _call_llm_raw(final_prompt_text)
#     try:
#         parsed = _parse_json_from_llm_response(raw)
#     except ValueError as e:
#         return {"execution_raw": raw, "error": str(e)}
#     return {"execution_raw": raw, "execution_parsed": parsed}


# def run_pipeline(analyzer_prompt_objs: List[Dict[str, Any]],
#                  placeholder_values: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
#     """
#     Run analyzer -> optionally execute final_prompt.
#     """
#     outputs = []
#     for obj in analyzer_prompt_objs:
#         result: Dict[str, Any] = {"task": obj.get("task")}
        
#         # 1. Analyze (Federation Phase)
#         analyzer_res = analyze_with_llm(obj)
#         result.update(analyzer_res)

#         if "error" in analyzer_res:
#             outputs.append(result)
#             continue

#         final_prompt = analyzer_res["analyzer_parsed"]["final_prompt"]
#         result["final_prompt"] = final_prompt

#         if not placeholder_values:
#             # no execution stage requested
#             outputs.append(result)
#             continue

#         # 2. Execution Phase
#         # Substitute placeholders (using the robust regex function)
#         substituted = substitute_placeholders_with_json_arrays(final_prompt, placeholder_values)
#         result["final_prompt_substituted"] = substituted

#         # Execute final prompt
#         exec_res = execute_final_prompt(substituted)
#         result.update(exec_res)

#         # Filter execution_parsed to keep only requested languages (if available)
#         parsed = exec_res.get("execution_parsed") or exec_res.get("parsed") or None
#         if parsed is not None:
#             # Try to identify which list in placeholder_values corresponds to 'languages'
#             requested_vals = []
#             for ph_key, ph_val in placeholder_values.items():
#                 if "language" in ph_key.lower():
#                     requested_vals = ph_val if isinstance(ph_val, (list, tuple)) else [ph_val]
#                     break
            
#             if requested_vals:
#                 requested_vals = [str(x) for x in requested_vals]
#                 filtered = filter_execution_result_to_requested(parsed, requested_vals)
#                 result["execution_parsed_filtered"] = filtered

#         outputs.append(result)

#     return outputs  


# # Quick test runner (if run directly)
# if __name__ == "__main__":
#     from C_federator_LLM import build_analyzer_prompts_from_plan

#     demo_plan = {
#         "db_llm": [
#             "For the languages <languages>, find the Indian states where they are native, and the capitals of those Indian states."
#         ]
#     }

#     print("Building analyzer prompts...")
#     analyzer_objs = build_analyzer_prompts_from_plan(demo_plan)
    
#     # Example placeholder values collected from db_user execution
#     # Note: Deliberately using lower case key to test case-insensitive matching with <languages> or <Languages>
#     placeholder_values = {"languages": ["Assamese", "Bengali", "Telugu"]}

#     print("Running pipeline...")
#     out = run_pipeline(analyzer_objs, placeholder_values=placeholder_values)
    
#     print("\n=== FINAL PIPELINE OUTPUT ===\n")
#     print(json.dumps(out, indent=2, ensure_ascii=False))

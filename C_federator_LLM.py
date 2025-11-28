"""
DB-LLM prompt *builder* (federation side).
This module only *builds* analyzer prompts (no LLM calls). Keep it light and deterministic.
"""

import json
import re
from typing import List, Dict, Any

PLACEHOLDER_RE = re.compile(r"<[^>]+>")

ANALYZER_TEMPLATE = """
You are a prompt-engineering assistant.

I will give you a natural-language instruction (TASK) that may contain placeholders like <languages>, <cities>, <states>, <cuisines>, etc.

Your job is to produce a strict, machine-friendly *final prompt* for a second LLM (the execution LLM). The final prompt MUST:

1. Keep placeholders unchanged (e.g. "<languages>"), do NOT substitute them here.
2. Clearly state what each placeholder means and the expected format (e.g. list of strings).
3. Specify the exact JSON schema the execution LLM must return when placeholders are replaced.
4. Provide a short concrete example demonstrating the input placeholders and the expected JSON output.
5. Instruct the execution LLM to output ONLY valid JSON (no explanations, no markdown, no code fences).

Return a JSON object (ONLY JSON) with these fields:
{{
  "task": "{task}",
  "placeholders": {placeholders},
  "final_prompt": "<the final prompt text to send to the execution LLM (placeholders intact)>",
  "notes": "<brief optional notes>"
}}
""".strip()


def detect_placeholders(text: str) -> List[str]:
    return list(dict.fromkeys(PLACEHOLDER_RE.findall(text)))


def build_analyzer_prompt(task: str) -> Dict[str, Any]:
    placeholders = detect_placeholders(task)
    analyzer_prompt = ANALYZER_TEMPLATE.format(task=task, placeholders=json.dumps(placeholders))
    return {"task": task, "placeholders": placeholders, "analyzer_prompt": analyzer_prompt}


def build_analyzer_prompts_from_plan(plan_or_tasks: Any) -> List[Dict[str, Any]]:
    """
    Accepts either a plan (dict with 'db_llm') or a list of task strings.
    Returns list of analyzer prompt objects (no LLM calls).
    """
    tasks = []
    if isinstance(plan_or_tasks, dict):
        tasks = plan_or_tasks.get("db_llm", []) or plan_or_tasks.get("db_llm_structured", [])
    elif isinstance(plan_or_tasks, list):
        tasks = plan_or_tasks
    else:
        raise ValueError("Input must be a plan dict or a list of db_llm task strings.")

    return [build_analyzer_prompt(t) for t in tasks]


# Quick self-test
if __name__ == "__main__":
    demo = {
        "db_llm": [
            "For the languages <languages>, find the Indian states and countries where they are native, and the capitals of those Indian states."
        ]
    }
    print(json.dumps(build_analyzer_prompts_from_plan(demo), indent=2, ensure_ascii=False))

from prompter import get_prompt
from context import ItineraryPlannerContext
from steps import ask_llm
import inspect
import dataclasses
import types
import json
import re
from steps import add_demo_data,extract_data_from_user_profile

def context_to_string(context):
    """
    Accepts:
      - a class (with annotations or class-level defaults)
      - an instance (normal object, dataclass instance, or pydantic model instance)
    Returns a JSON string of the "useful" key:value pairs (filters out internals).
    """
    # Helper to convert dict values safely to JSON (fallback to str)
    def dumps_safe(d):
        return json.dumps(d, default=str, ensure_ascii=False)

    # ---------- Instance ----------
    if not inspect.isclass(context):
        # dataclass instance
        if dataclasses.is_dataclass(context):
            return dumps_safe(dataclasses.asdict(context))

        # pydantic instance (v1 or v2)
        try:
            from pydantic import BaseModel
        except Exception:
            BaseModel = None

        if BaseModel and isinstance(context, BaseModel):
            # pydantic v1 has .dict(), v2 has .model_dump()
            if hasattr(context, "dict"):
                return dumps_safe(context.dict())
            if hasattr(context, "model_dump"):
                return dumps_safe(context.model_dump())

        # general instance: use __dict__ / vars and drop private keys
        if hasattr(context, "__dict__"):
            data = {k: v for k, v in context.__dict__.items() if not k.startswith("_")}
            return dumps_safe(data)

        # last-resort: try vars()
        try:
            data = {k: v for k, v in vars(context).items() if not k.startswith("_")}
            return dumps_safe(data)
        except Exception:
            return str(context)

    # ---------- Class ----------
    cls = context

    # dataclass *class* (fields may have defaults)
    if dataclasses.is_dataclass(cls):
        out = {}
        for f in dataclasses.fields(cls):
            out[f.name] = getattr(cls, f.name, None)
        return dumps_safe(out)

    # If class uses annotations (PEP 526), prefer annotated names (this avoids inherited framework attrs)
    ann = getattr(cls, "__annotations__", None)
    if ann:
        out = {}
        for name in ann:
            if name.startswith("_"):
                continue
            out[name] = getattr(cls, name, None)
        return dumps_safe(out)

    # Fallback: inspect cls.__dict__ but filter internals and descriptors
    out = {}
    for k, v in cls.__dict__.items():
        if k.startswith("_"):
            continue
        if inspect.isroutine(v):
            continue
        # skip descriptors and common class-level wrappers
        if isinstance(v, (types.ModuleType, type, staticmethod, classmethod, property)):
            continue
        out[k] = v
    return dumps_safe(out)

#Remove Not NULL

# print(context_to_string(ItineraryPlannerContext))

# prompt = get_prompt('sql2', context=context_to_string(ItineraryPlannerContext),user_id = '1')

# print(prompt)
# response = ask_llm(prompt)
# print(response)


def extract_sql(response: str) -> str:
    match = re.search(r'(SELECT[\s\S]*?;)', response, re.IGNORECASE)
    if match:
        sql = match.group(1).strip()
        sql = sql.replace('```sql', '').replace('```', '').strip()
        return sql
    return ""

# print(extract_sql(response))
from typing import List
from decimal import Decimal


user_id = add_demo_data()
prof = extract_data_from_user_profile(user_id)
print(prof)
# decomposer.py
import os, json, re
from typing import Type

from steps import ask_llm
from prompter import get_prompt,PROMPT_TEMPLATES
from context import (
    TripSuggestionContext, ItineraryPlannerContext, ReviewSummarizerContext,
    MeetingPointContext, RouteOptimizerContext, TripJournalContext,BaseContext  
)


CONTEXT_MAPPING = {
    "TripSuggestion": TripSuggestionContext,
    "ItineraryPlanner": ItineraryPlannerContext,
    "ReviewSummarizer": ReviewSummarizerContext,
    "MeetingPointPlanner": MeetingPointContext,
    "RouteOptimizer": RouteOptimizerContext,
    "TripJournalManager": TripJournalContext,
}


class Decomposer:
    def __init__(self, query: str, task: str):
        print(f"[Decomposer] Initializing for task: {task}")
        self.query = query
        self.task = task
        self.context_class: Type[BaseContext]
        self.prompt: str = ""

        self.load_prompt_and_context()

    def load_prompt_and_context(self):
        print("[Decomposer] Loading prompt and context...")
        if self.task not in PROMPT_TEMPLATES:
            raise ValueError(f"[Error] No prompt found for task: {self.task}")
        if self.task not in CONTEXT_MAPPING:
            raise ValueError(f"[Error] No context schema found for task: {self.task}")

        self.prompt = PROMPT_TEMPLATES[self.task].format(query=self.query)
        self.context_class = CONTEXT_MAPPING[self.task]

        print(f"[Decomposer] Loaded prompt and context for task: {self.task}")


    def run(self):
        print("[Decomposer] Sending prompt to LLM...")

        llm_response = ask_llm(self.prompt)

        print("[Decomposer] LLM response received.")
        print("[Decomposer] Building initial context object. Extracting JSON...")

        # Extract JSON from LLM response using regex
        match = re.search(r'\{.*\}', llm_response, flags=re.DOTALL)
        if match:
            cleaned = match.group(0)
            data = json.loads(cleaned)
        else:
            raise ValueError(f"Cannot parse JSON from LLM response: {llm_response}")

        #Using Pydantic here.
        # context = ItineraryPlannerContext.model_validate(data)
        context = self.context_class.model_validate(data)


        print(f"[Decomposer] Context Object:\n{context}")
        print("[Decomposer] Context successfully built.\n")
        return context


if __name__ == "__main__":
    demo_query = "Plan a 2 day itinerary in Jaipur covering Amer Fort and City Palace with a budget of 5000 INR."
    task_name = "ItineraryPlanner"

    decomposer = Decomposer(query=demo_query, task=task_name)
    context = decomposer.run()

    print("\n[Final Context Returned]")
    print(context)
    print()

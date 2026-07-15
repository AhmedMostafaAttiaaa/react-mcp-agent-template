import json
import re
from dataclasses import dataclass
from typing import Optional

_THOUGHT_RE = re.compile(r"Thought:\s*(.*?)(?=\n(?:Action|Final Answer):|\Z)", re.DOTALL)
_ACTION_RE = re.compile(r"Action:\s*(.+)")
_ACTION_INPUT_RE = re.compile(r"Action Input:\s*(\{.*?\})", re.DOTALL)
_FINAL_RE = re.compile(r"Final Answer:\s*(.*)", re.DOTALL)


@dataclass
class ReActStep:
    thought: str = ""
    action: Optional[str] = None
    action_input: Optional[dict] = None
    final_answer: Optional[str] = None
    raw: str = ""
    error: Optional[str] = None

    @property
    def is_final(self) -> bool:
        return self.final_answer is not None

    @property
    def is_action(self) -> bool:
        return self.action is not None and self.final_answer is None


def parse_react_step(text: str) -> ReActStep:
    """Parses raw LLM output into a ReActStep. Never raises — malformed output is
    surfaced via `.error` so the agent loop can feed a corrective Observation back
    to the model instead of crashing the run.
    """
    step = ReActStep(raw=text)

    thought_match = _THOUGHT_RE.search(text)
    if thought_match:
        step.thought = thought_match.group(1).strip()

    final_match = _FINAL_RE.search(text)
    if final_match:
        step.final_answer = final_match.group(1).strip()
        return step

    action_match = _ACTION_RE.search(text)
    if not action_match:
        step.error = "Could not find 'Action:' or 'Final Answer:' in model output."
        if not step.thought:
            step.thought = text.strip()
        return step

    step.action = action_match.group(1).strip()

    input_match = _ACTION_INPUT_RE.search(text)
    if not input_match:
        step.error = "Action given but no 'Action Input:' found."
        return step

    raw_input = input_match.group(1).strip()
    try:
        step.action_input = json.loads(raw_input)
    except json.JSONDecodeError as exc:
        step.error = f"Malformed Action Input JSON: {exc}"

    return step

import json
from datetime import datetime, timezone
from pathlib import Path

from .guardrails import InputGuard
from .mcp_client import MCPClient
from .parser import parse_react_step
from .prompt_builder import PromptBuilder
from .skill_router import KeywordRouter, load_skills

_REFUSAL_MESSAGE = "I can't help with that request."


class Agent:
    """Provider-agnostic ReAct loop. Takes any Provider implementing generate()/
    list_models() (see agent/providers/base.py) and drives Thought/Action/
    Action Input/Observation cycles against MCP tools filtered by the skill router.
    """

    def __init__(self, config: dict, provider):
        self.config = config
        self.provider = provider
        self.prompt_builder = PromptBuilder(config["base_prompt_path"])
        skills = load_skills(config["skills"]["directory"])
        self.router = KeywordRouter(skills, max_active_skills=config["skills"]["max_active_skills"])
        self.max_steps = config["max_steps"]
        self.traces_dir = Path(config["logging"]["traces_dir"])
        self.traces_dir.mkdir(parents=True, exist_ok=True)
        self.guard = InputGuard(config.get("safety", {}).get("blocklist_path", "agent/blocklist.txt"))

    async def run(self, user_input: str, on_step=None) -> str:
        block_reason = self.guard.check_input(user_input)
        if block_reason is not None:
            trace = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "user_input": user_input,
                "blocked": True,
                "block_reason": block_reason,
                "final_answer": _REFUSAL_MESSAGE,
            }
            self._write_trace(trace)
            if on_step:
                on_step(
                    {
                        "step": 0,
                        "thought": "",
                        "action": None,
                        "action_input": None,
                        "final_answer": _REFUSAL_MESSAGE,
                        "error": None,
                        "blocked": True,
                    }
                )
            return _REFUSAL_MESSAGE

        matched_skills = self.router.route(user_input)
        allowed_tool_names = {t for s in matched_skills for t in s.tools}

        trace = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_input": user_input,
            "matched_skills": [s.name for s in matched_skills],
            "steps": [],
        }

        servers = self.config["mcp"]["servers"]
        async with MCPClient(servers) as mcp_client:
            all_tools = await mcp_client.list_tools()
            # Tool filtering is skill-driven: only expose what the matched skill(s)
            # explicitly reference. Fall back to every tool if nothing matched, so
            # the agent isn't stranded on an unrecognized query.
            if allowed_tool_names:
                tools = [t for t in all_tools if t.name in allowed_tool_names]
            else:
                tools = all_tools

            tool_dicts = [
                {"name": t.name, "description": t.description, "input_schema": t.input_schema}
                for t in tools
            ]
            valid_tool_names = {t.name for t in tools}

            scratchpad = ""
            final_answer = None

            for step_num in range(1, self.max_steps + 1):
                prompt = self.prompt_builder.build(user_input, matched_skills, tool_dicts, scratchpad)
                result = self.provider.generate(prompt, stop=["Observation:"])
                step = parse_react_step(result.text)

                step_record = {
                    "step": step_num,
                    "thought": step.thought,
                    "action": step.action,
                    "action_input": step.action_input,
                    "final_answer": step.final_answer,
                    "error": step.error,
                    "raw": step.raw,
                }

                if step.final_answer is not None:
                    final_answer = step.final_answer
                    trace["steps"].append(step_record)
                    if on_step:
                        on_step(step_record)
                    break

                if step.error or step.action is None:
                    observation = (
                        f"Error: {step.error or 'no action given'}. Reformat your response using "
                        "Thought/Action/Action Input, or Final Answer."
                    )
                elif step.action not in valid_tool_names:
                    observation = f"Error: '{step.action}' is not an available tool. Choose from: {sorted(valid_tool_names)}."
                else:
                    try:
                        observation = await mcp_client.call_tool(step.action, step.action_input or {})
                        observation = self.guard.sanitize_observation(observation)
                    except Exception as exc:
                        observation = f"Error calling tool '{step.action}': {exc}"

                step_record["observation"] = observation
                trace["steps"].append(step_record)
                if on_step:
                    on_step(step_record)

                scratchpad += (
                    f"\nThought: {step.thought}\nAction: {step.action}\n"
                    f"Action Input: {json.dumps(step.action_input)}\nObservation: {observation}\n"
                )

            if final_answer is None:
                final_answer = (
                    "I hit the step limit before reaching a confident final answer.\n\n"
                    "What I found so far:\n" + (scratchpad or "No progress was made.") +
                    "\n\nWhat's uncertain: I ran out of reasoning steps before I could verify a complete answer."
                )
                trace["hit_max_steps"] = True

        trace["final_answer"] = final_answer
        self._write_trace(trace)
        return final_answer

    def _write_trace(self, trace: dict) -> None:
        filename = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f") + "Z.json"
        path = self.traces_dir / filename
        path.write_text(json.dumps(trace, indent=2, default=str), encoding="utf-8")

from pathlib import Path


class PromptBuilder:
    """Assembles the per-turn system prompt from three layers: a fixed ReAct base
    prompt, the currently matched Skill(s), and only the tool schemas those Skills
    reference — plus the running Thought/Action/Observation scratchpad.
    """

    def __init__(self, base_prompt_path: str):
        self.base_prompt = Path(base_prompt_path).read_text(encoding="utf-8")

    def build(self, user_input: str, skills: list, tools: list, scratchpad: str) -> str:
        sections = [self.base_prompt]

        if skills:
            skills_text = "\n\n".join(f"## Skill: {s.name}\n{s.content}" for s in skills)
            sections.append(f"# Active Skills\n\n{skills_text}")
        else:
            sections.append("# Active Skills\n\nNone matched — rely on general reasoning and the available tools.")

        if tools:
            tools_text = "\n".join(
                f"- {t['name']}: {t.get('description', '')} (args schema: {t.get('input_schema', {})})"
                for t in tools
            )
        else:
            tools_text = "None available."
        sections.append(f"# Available tools\n\n{tools_text}")

        sections.append(f"# Task\n\nQuestion: {user_input}")

        if scratchpad:
            sections.append("# Scratchpad so far\n" + scratchpad)

        return "\n\n".join(sections)

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

import yaml

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


@dataclass
class Skill:
    name: str
    triggers: list = field(default_factory=list)
    tools: list = field(default_factory=list)
    content: str = ""
    path: Path = None


def load_skills(skills_dir: str) -> list:
    """Loads every *.md file in skills_dir (except README.md) as a Skill: YAML
    frontmatter for metadata, everything after the closing '---' as prompt content.
    """
    skills = []
    for path in sorted(Path(skills_dir).glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        text = path.read_text(encoding="utf-8")
        match = _FRONTMATTER_RE.match(text)
        if not match:
            raise ValueError(f"Skill file {path} is missing YAML frontmatter delimited by '---'.")
        meta = yaml.safe_load(match.group(1)) or {}
        content = match.group(2).strip()
        skills.append(
            Skill(
                name=meta.get("name", path.stem),
                triggers=[str(t).lower() for t in meta.get("triggers", [])],
                tools=list(meta.get("tools", [])),
                content=content,
                path=path,
            )
        )
    return skills


class BaseSkillRouter(ABC):
    """Interface routers must implement, so a future EmbeddingRouter can be swapped
    in for KeywordRouter without touching anything that calls .route().
    """

    @abstractmethod
    def route(self, user_input: str) -> list:
        ...


class KeywordRouter(BaseSkillRouter):
    """Matches skills via case-insensitive substring matching against trigger
    phrases. Cheap, fully offline, zero dependencies beyond the stdlib — but
    multi-word phrases must be listed as explicit triggers (e.g. "look up"),
    since this does not tokenize or stem; "look" alone will not match "look up"
    unless "look" itself is also a trigger.
    """

    def __init__(self, skills: list, max_active_skills: int = 2):
        self.skills = skills
        self.max_active_skills = max_active_skills

    def route(self, user_input: str) -> list:
        text = user_input.lower()
        matched = [skill for skill in self.skills if any(trigger in text for trigger in skill.triggers)]
        return matched[: self.max_active_skills]

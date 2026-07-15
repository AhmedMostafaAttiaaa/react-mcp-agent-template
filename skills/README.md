# Skills

A skill is a markdown file with YAML frontmatter that tells the router:

- `name` — a short identifier, shown in traces.
- `triggers` — a list of lowercase keyword/phrase strings. If any trigger is a substring of the
  user's (lowercased) input, the skill is considered matched. Matching is plain, untokenized
  substring matching — multi-word phrases must be listed explicitly (e.g. `"look up"`), a single
  word is never implicitly split out of a phrase you didn't also list.
- `tools` — the exact MCP tool names this skill is allowed to expose to the agent. Only tools
  referenced by a matched skill are shown to the model that turn; if no skill matches, every
  available tool is shown as a fallback so the agent isn't stranded.

Everything below the closing `---` is markdown instructions injected into the agent's prompt when
the skill is active — explain when and how to use the tools it lists.

Up to `skills.max_active_skills` (see `config.yaml`) skills can be active in a single turn, in the
order they matched.

See `example_skill.md` and `rag_skill.md` for working examples.

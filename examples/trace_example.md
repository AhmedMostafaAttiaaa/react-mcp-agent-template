# Example trace

Traces are written to `traces/<timestamp>.json` after every `run.py` call or UI turn. Here's a
trimmed example for the question **"What's 12 plus 30, and what time is it?"** with
`provider: ollama`.

```json
{
  "timestamp": "2026-01-01T12:00:00+00:00",
  "user_input": "What's 12 plus 30, and what time is it?",
  "matched_skills": ["math_and_time"],
  "steps": [
    {
      "step": 1,
      "thought": "I need to add 12 and 30 first.",
      "action": "add",
      "action_input": {"a": 12, "b": 30},
      "observation": "42"
    },
    {
      "step": 2,
      "thought": "Now I need the current time.",
      "action": "get_current_time",
      "action_input": {},
      "observation": "2026-01-01T12:00:00+00:00"
    },
    {
      "step": 3,
      "thought": "I have both answers now.",
      "final_answer": "12 + 30 = 42, and the current UTC time is 2026-01-01T12:00:00+00:00."
    }
  ],
  "final_answer": "12 + 30 = 42, and the current UTC time is 2026-01-01T12:00:00+00:00."
}
```

Use these traces to compare providers/models on the same task: run the same question with
`provider: ollama` and `provider: groq`, then diff the `steps` arrays — step count, which tools
were chosen, and whether the parser had to fall back (a non-null `error` field on any step) are
all good signals for which model handles your Skills better.

from agent.parser import parse_react_step


def test_parses_final_answer():
    text = "Thought: I know this.\nFinal Answer: The sky is blue."
    step = parse_react_step(text)
    assert step.thought == "I know this."
    assert step.final_answer == "The sky is blue."
    assert step.is_final
    assert step.error is None


def test_parses_action_and_input():
    text = (
        "Thought: I need to look this up.\n"
        "Action: search_docs\n"
        'Action Input: {"query": "revenue Q1"}\n'
    )
    step = parse_react_step(text)
    assert step.thought == "I need to look this up."
    assert step.action == "search_docs"
    assert step.action_input == {"query": "revenue Q1"}
    assert step.is_action
    assert step.error is None


def test_fails_soft_on_malformed_output():
    text = "I think the answer is 42 but I forgot the format."
    step = parse_react_step(text)
    assert step.action is None
    assert step.final_answer is None
    assert step.error is not None
    assert step.thought  # falls back to the raw text instead of crashing


def test_fails_soft_on_malformed_action_input_json():
    text = "Thought: checking.\nAction: search_docs\nAction Input: {query: revenue}\n"
    step = parse_react_step(text)
    assert step.action == "search_docs"
    assert step.action_input is None
    assert step.error is not None


def test_missing_action_input_flagged():
    text = "Thought: checking.\nAction: search_docs\n"
    step = parse_react_step(text)
    assert step.action == "search_docs"
    assert step.action_input is None
    assert step.error is not None


def test_stops_at_observation_boundary():
    text = (
        "Thought: checking.\n"
        "Action: search_docs\n"
        'Action Input: {"query": "x"}\n'
        "Observation: this should never be produced by the model"
    )
    step = parse_react_step(text)
    assert step.action == "search_docs"
    assert step.action_input == {"query": "x"}

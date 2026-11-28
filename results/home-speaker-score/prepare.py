"""Build stand-alone OpenRouter request bodies from the archived dialogues."""
import json
from pathlib import Path

here = Path(__file__).resolve().parent
names = {"A": "glm", "B": "qwen", "C": "deepseek", "D": "gemma", "E": "fable"}
for alias, name in names.items():
    folder = "natural-chat-alexander-oral-v2-20261128" if name in ("qwen", "gemma") else "natural-chat-frontier-20261128"
    if name == "fable":
        messages = json.loads((here.parent / folder / "fable-run.json").read_text())["messages"][1:]
    else:
        raw = json.loads((here.parent / folder / "raw.json").read_text())
        messages = raw["conversations"][name]["messages"][1:]
    turns = [{"turn": i + 1, "user": messages[2*i]["content"], "device": messages[2*i+1]["content"]} for i in range(6)]
    body = {"model": "x-ai/grok-4.3", "temperature": 0, "max_tokens": 1800,
            "reasoning": {"effort": "none"}, "response_format": {"type": "json_object"},
            "provider": {"require_parameters": True, "max_price": {"prompt": 1.25, "completion": 2.5}},
            "messages": [{"role": "system", "content": (here / "judge.txt").read_text()},
                         {"role": "user", "content": json.dumps(turns, ensure_ascii=False)}]}
    (here / "requests" / f"{alias}.json").write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n")

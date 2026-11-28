"""Print published scores and their equal-weight means without network calls."""
from pathlib import Path
import json

root = Path(__file__).resolve().parent
audit = json.loads((root / "audit.json").read_text())
criteria = ("understanding", "usefulness", "spoken")
for alias, row in audit.items():
    request = json.loads((root / "requests" / (alias + ".json")).read_text())
    turns = json.loads(request["messages"][1]["content"])
    response = json.loads((root / (alias + "-response.json")).read_text())
    choice = response["choices"][0]
    assert choice["finish_reason"] == "stop"
    verdict = json.loads(choice["message"]["content"])
    for method, values in [("API", [verdict[k]["score"] for k in criteria]), ("review", row["scores"])]:
        assert len(values) == 3 and all(type(x) is int and 1 <= x <= 5 for x in values)
        print(row["model"], method, values, f"{sum(values)/3:.2f}")
    for k in criteria:
        item = verdict[k]
        if item["quote"] not in turns[item["turn"]-1]["device"]:
            print("Quote mismatch:", alias, k)

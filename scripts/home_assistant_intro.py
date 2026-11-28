"""Print the test matrix or one Chat Completions request. No network calls."""
import argparse
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = json.loads((root / "testsets/home-assistant-intro.json").read_text())
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--request", nargs=3, metavar=("CASE", "PROFILE", "MODEL"))
args = parser.parse_args()
if args.request:
    case_id, profile, model = args.request
    case = next((item for item in spec["cases"] if item["id"] == case_id), None)
    if case is None or profile not in case["profiles"]:
        parser.error("Unknown case/profile combination. Run without arguments to list cases.")
    prompt = (root / "prompts/natural-voice-assistant-v2.txt").read_text().strip()
    system = "\n\n".join((prompt, spec["station"], spec["profiles"][profile]))
    messages = [{"role": "system", "content": system}, {"role": "user", "content": case["ask"]}]
    print(json.dumps({"model": model, "messages": messages}, ensure_ascii=False, indent=2))
else:
    for case in spec["cases"]:
        for profile in case["profiles"]:
            print(case["id"], profile, case["ask"], sep="\t")

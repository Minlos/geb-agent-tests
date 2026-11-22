#!/bin/zsh
cd -- "${0:A:h}" || exit 1
python3 openrouter_smoke.py
result=$?
read -r "?Press Return to close. "
exit "$result"

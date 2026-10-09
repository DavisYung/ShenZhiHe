# -*- coding: utf-8 -*-
import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")
q = json.load(io.open("f6chem/quiz/chem/2a.json", encoding="utf-8"))
for x in q["questions"]:
    if x["id"] == "2a-q26":
        print(json.dumps(x, ensure_ascii=False, indent=1))
import os
import json

DATA_DIR = "data/politicians"

def load_all_politicians():
    politicians = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(DATA_DIR, filename), encoding="utf-8") as f:
                data = json.load(f)
                politicians.append(data)
    return politicians

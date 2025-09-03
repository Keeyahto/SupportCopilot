import json
import os
from pathlib import Path
from typing import Any, List, Dict


# Определяем путь к данным в зависимости от окружения
if os.getenv("TESTING") == "true":
    # В тестах используем относительный путь от корня проекта
    DATA_DIR = Path("data/mock")
else:
    # В production используем абсолютный путь
    DATA_DIR = Path("/app/data/mock")


def load_json(name: str) -> List[Dict[str, Any]]:
    p = DATA_DIR / name
    if not p.exists():
        return []
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


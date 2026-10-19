#!/usr/bin/env python3
"""No destructive operations. Validate bundled GUI and updater."""
import ast
from pathlib import Path
p=Path(__file__).parents[1]
ast.parse((p/"desktop"/"nexora-center.py").read_text(encoding="utf-8"))
text=(p/"desktop"/"nexora-center.py").read_text(encoding="utf-8")
for name in ("Магазин приложений", "Обновление системы", "Установить Nexora", "Интернет"):
    assert name in text, f"Missing Russian label: {name}"
assert "shell=True" not in text
update=(p/"desktop"/"nexora-update").read_text(encoding="utf-8")
assert "apt-get update" in update and "apt-get upgrade" in update
assert "pkexec" in update
print("Nexora Center and updater static tests passed")

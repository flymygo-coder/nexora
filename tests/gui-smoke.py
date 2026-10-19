#!/usr/bin/env python3
"""Launch Nexora Center in Xvfb, exercise theme switching, capture a real screenshot."""
from pathlib import Path
import importlib.util
from PIL import ImageGrab
import tkinter as tk

root = Path(__file__).resolve().parents[1]
module_file = root / "desktop" / "nexora-center.py"
spec = importlib.util.spec_from_file_location("nexora_center", module_file)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ui = module.Center()
try:
    ui.root.update_idletasks()
    ui.root.update()
    assert ui.root.title() == "Nexora — центр системы"
    assert ui.root.winfo_width() >= 760
    assert len(module.buttons) == 8
    assert set(module.COMMANDS) == {x[0] for x in module.buttons}
    assert ui.theme == "dark"
    ui.toggle()
    ui.root.update_idletasks()
    ui.root.update()
    assert ui.theme == "light"
    ui.toggle()
    ui.root.update_idletasks()
    ui.root.update()
    assert ui.theme == "dark"
    shot = root / "artifacts" / "nexora-center-xvfb.png"
    shot.parent.mkdir(exist_ok=True)
    x, y = ui.root.winfo_rootx(), ui.root.winfo_rooty()
    w, h = ui.root.winfo_width(), ui.root.winfo_height()
    ImageGrab.grab(bbox=(x, y, x+w, y+h)).save(shot)
    assert shot.stat().st_size > 15000
    print("PASS: Nexora Center GUI launched, widgets rendered, light/dark themes changed")
    print("Screenshot:", shot)
finally:
    ui.root.destroy()

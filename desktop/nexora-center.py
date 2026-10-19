#!/usr/bin/env python3
"""Nexora Center — Russian-language launcher for the supported Linux preview."""
import os
import shutil
import subprocess
import tkinter as tk
from tkinter import messagebox

COMMANDS = {
    "store": [["gnome-software"], ["synaptic"]],
    "browser": [["firefox-esr"], ["firefox"]],
    "files": [["thunar"]],
    "office": [["libreoffice"]],
    "settings": [["xfce4-settings-manager"]],
    "terminal": [["xfce4-terminal"]],
    "updates": [["xfce4-terminal", "--hold", "--command=/usr/local/sbin/nexora-update"]],
    "installer": [["calamares"]],
}
COLORS = {
    "dark": {"bg": "#0B1225", "card": "#192543", "fg": "#F2F6FF", "muted": "#B1BCD2", "accent": "#477DE6"},
    "light": {"bg": "#EFF3FA", "card": "#FFFFFF", "fg": "#172342", "muted": "#59657C", "accent": "#3569D5"},
}
buttons = [
    ("store", "Магазин приложений", "Linux-программы и Flatpak"),
    ("browser", "Интернет", "Браузер Firefox"),
    ("files", "Мои файлы", "Папки и документы"),
    ("office", "Офис", "LibreOffice"),
    ("updates", "Обновление системы", "Проверить пакеты и безопасность"),
    ("settings", "Параметры", "Настройки рабочего стола"),
    ("terminal", "Терминал", "Системные инструменты"),
    ("installer", "Установить Nexora", "Установка Live-системы на диск"),
]

class Center:
    def __init__(self):
        self.theme = "dark"
        self.root = tk.Tk()
        self.root.title("Nexora — центр системы")
        self.root.geometry("990x665")
        self.root.minsize(760, 570)
        self.root.configure(bg=COLORS[self.theme]["bg"])
        self.draw()

    def launch(self, key):
        for argv in COMMANDS[key]:
            if shutil.which(argv[0]):
                try:
                    subprocess.Popen(argv, close_fds=True, start_new_session=True)
                    return
                except OSError as exc:
                    messagebox.showerror("Ошибка запуска", str(exc))
                    return
        messagebox.showwarning("Приложение не найдено", "Этот компонент не установлен в текущей системе.")

    def toggle(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.draw()

    def draw(self):
        c = COLORS[self.theme]
        for child in self.root.winfo_children():
            child.destroy()
        main = tk.Frame(self.root, bg=c["bg"], padx=36, pady=26)
        main.pack(fill="both", expand=True)
        header = tk.Frame(main, bg=c["bg"])
        header.pack(fill="x")
        tk.Label(header, text="NEXORA", font=("DejaVu Sans", 28, "bold"),
                 bg=c["bg"], fg=c["fg"]).pack(side="left")
        tk.Button(header, text="Сменить тему", command=self.toggle, bg=c["card"],
                  fg=c["fg"], relief="flat", padx=14, pady=9, cursor="hand2").pack(side="right")
        tk.Label(main, text="Центр системы", font=("DejaVu Sans", 19, "bold"),
                 bg=c["bg"], fg=c["fg"], anchor="w", pady=20).pack(fill="x")
        tk.Label(main, text="Все основные программы, настройки и обновления — в одном месте.",
                 font=("DejaVu Sans", 11), bg=c["bg"], fg=c["muted"], anchor="w").pack(fill="x")
        grid = tk.Frame(main, bg=c["bg"])
        grid.pack(fill="both", expand=True, pady=(25, 8))
        for col in range(2):
            grid.grid_columnconfigure(col, weight=1, uniform="cards")
        for row in range(4):
            grid.grid_rowconfigure(row, weight=1)
        for i, (key, title, subtitle) in enumerate(buttons):
            card = tk.Frame(grid, bg=c["card"], padx=20, pady=15)
            card.grid(row=i // 2, column=i % 2, sticky="nsew", padx=6, pady=6)
            tk.Button(card, text=title, anchor="w", command=lambda k=key: self.launch(k),
                      relief="flat", bg=c["card"], fg=c["fg"], activebackground=c["card"],
                      activeforeground=c["accent"], font=("DejaVu Sans", 13, "bold"),
                      cursor="hand2").pack(fill="x")
            tk.Label(card, text=subtitle, anchor="w", bg=c["card"], fg=c["muted"],
                     font=("DejaVu Sans", 10)).pack(fill="x")
        footer = tk.Frame(main, bg=c["bg"])
        footer.pack(fill="x")
        tk.Label(footer, text="Linux Edition • Тестовый выпуск • Основа Debian 13",
                 bg=c["bg"], fg=c["muted"], font=("DejaVu Sans", 9)).pack(side="left")
        tk.Label(footer, text="Обновления ОС через APT", bg=c["bg"],
                 fg=c["muted"], font=("DejaVu Sans", 9)).pack(side="right")

if __name__ == "__main__":
    Center().root.mainloop()

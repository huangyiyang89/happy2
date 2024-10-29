import tkinter as tk
from tkinter import ttk
import happy
import happy.interface
import happy.scripts
import happy.scripts.autoload
import pkgutil
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Happy Scripts Manager")
        self.create_widgets()

    def create_widgets(self):
        self.ui_container = ttk.Frame(self.root)
        self.ui_container.pack(fill=tk.BOTH, expand=True)

        self.update_button = ttk.Button(self.root, text="更新UI", command=self.update_ui_container)
        self.update_button.pack(pady=10)

    def update_ui_container(self):
        """更新UI元素"""
        for widget in self.ui_container.winfo_children():
            widget.destroy()

        for cg in happy.open_all():
            cg.load_script(happy.scripts.AutoBattle)
            cg.load_script(happy.scripts.SpeedBattle)
            cg.load_script(happy.scripts.SpeedMove)
            cg.load_script(happy.scripts.Assistant)
            cg.load_script(happy.scripts.AutoEncounter)
            cg.load_script(happy.scripts.LevelUp)
            cg.load_script(happy.scripts.AutoMaze)
            cg.load_script(happy.scripts.mission.Szdjz)
            cg.load_script(happy.scripts.util.Logger)
            cg.load_script(happy.scripts.util.Neixin)

            for _, module_name, _ in pkgutil.iter_modules(happy.scripts.autoload.__path__):
                module = __import__(f"happy.scripts.autoload.{module_name}", fromlist=["*"])
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, happy.interface.Script) and attr is not happy.interface.Script:
                        cg.load_script(attr)

            player_frame = ttk.LabelFrame(self.ui_container, text="Player Info")
            player_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

            ttk.Label(player_frame, text=f"Player Name: {cg.player.name}").pack(anchor=tk.W, padx=10, pady=2)
            ttk.Label(player_frame, text=f"Account: {cg.account}").pack(anchor=tk.W, padx=10, pady=2)

            scripts_frame = ttk.LabelFrame(player_frame, text="Scripts")
            scripts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

            for script in cg._scripts:
                ttk.Label(scripts_frame, text=script.__class__.__name__).pack(anchor=tk.W, padx=10, pady=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
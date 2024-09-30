import tkinter as tk
import happy
import happy.scripts


for cg in happy.open_all():
    cg.load_script(happy.scripts.AutoBattle)
    cg.load_script(happy.scripts.SpeedBattle)
    cg.load_script(happy.scripts.SpeedMove)
    cg.load_script(happy.scripts.Assistant)
    cg.load_script(happy.scripts.AutoEncounter)
    cg.load_script(happy.scripts.LevelUp)
    cg.load_script(happy.scripts.AutoMaze)
    cg.load_script(happy.scripts.farm.LiDong)

root = tk.Tk()
root.title("happy")

import happy
import logging
from nicegui import ui

import happy
import happy.scripts


logging.basicConfig(
    # filename="unhappy.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def update_ui_container():
    """更新UI元素"""

    ui_container.clear()
    with ui_container:
        for cg in happy.open_all():
            cg.load_script(happy.scripts.AutoBattle)
            cg.load_script(happy.scripts.SpeedBattle)
            cg.load_script(happy.scripts.SpeedMove)
            cg.load_script(happy.scripts.Assistant)
            cg.load_script(happy.scripts.AutoEncounter)
            cg.load_script(happy.scripts.LevelUp)
            cg.load_script(happy.scripts.AutoMaze)
            cg.load_script(happy.scripts.farm.LiDong)
            # cg.load_script(Szdjz, False)
            with ui.card():
                ui.label("Player Name").text = cg.player.name
                ui.label("Account").text = cg.account
                for script in cg._scripts:
                    ui.switch(script.name).bind_value(script, "enable")
    ui.update(ui_container)


def close_notify():
    happy.remove_open_limit()
    ui.notify("解除多开限制完成")


with ui.row():
    ui.button("解除多开限制", on_click=close_notify)
    refresh_button = ui.button("刷新", on_click=update_ui_container)

ui_container = ui.row()
ui.timer(1, update_ui_container, once=True)
ui.run(native=True, window_size=(760, 1000))

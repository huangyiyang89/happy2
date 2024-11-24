import happy
import logging
from nicegui import ui
import happy
import happy.interface
import happy.scripts
import happy.scripts.farm
import happy.scripts.farm.duoladong
import happy.scripts.farm.hadong
import happy.scripts.farm.lidong
import happy.scripts.farm.yanhuang
import happy.scripts.general
import happy.scripts.general.assistant
import happy.scripts.general.autobattle
import happy.scripts.general.speed
import happy.scripts.levelup
import happy.scripts.mission
import happy.scripts.mission.fushengruomeng


logging.basicConfig(
    # filename="unhappy.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def update_ui_container():
    """更新UI元素"""

    ui_container.clear()
    slot = 0
    with ui_container:
        for cg in happy.open_all():
            slot += 1
            cg.window.move_to_slot(slot)
            
            cg.load_script(happy.scripts.general.assistant.Assistant)
            cg.load_script(happy.scripts.general.autobattle.AutoBattle)
            cg.load_script(happy.scripts.general.speed.SpeedBattle)
            cg.load_script(happy.scripts.general.speed.SpeedMove)
            cg.load_script(happy.scripts.levelup.LevelUp)
            cg.load_script(happy.scripts.farm.lidong.Lidong)
            cg.load_script(happy.scripts.farm.yanhuang.Yanhuang)
            cg.load_script(happy.scripts.farm.duoladong.Duoladong)


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

ui.timer(0, update_ui_container, once=True)
ui.run(native=True, window_size=(900, 1000), reload=False)

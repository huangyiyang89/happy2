from happy.interface import Script
import logging

class Logger(Script):

    def _on_init(self):
        self.name = "日志记录"
        self.last_data = None
        self.last_content = None
        self.last_map_id = None

        self.printed = False
        self.enemy_max_hp = {}

    def _on_not_battle(self):

        pointer = self.cg.mem.read_int(0x0057A718)
        data = self.cg.mem.read_string(pointer, encoding="utf-8")
        dialog_content = self.cg.dialog.content
        
        if data and data != self.last_data:
            logging.info(data.replace("\n", ""))
            self.last_data = data

        if dialog_content and dialog_content != self.last_content:
            logging.info(dialog_content.replace("\n", ""))
            self.last_content = dialog_content

        if self.last_map_id != self.cg.map.id:
            logging.info(f"地图ID: {self.cg.map.id}")
            self.last_map_id = self.cg.map.id

        self.printed = False

    def _on_battle(self):
        if not self.printed:
            for unit in self.cg.battle.units.enemies:
                if unit.name not in self.enemy_max_hp or unit.hp_max > self.enemy_max_hp[unit.name]:
                    self.enemy_max_hp[unit.name] = unit.hp_max
            logging.info(f"敌人最大HP: {self.enemy_max_hp}")
            self.printed = True
from happy.interface import Script
import logging
import time

class Logger(Script):

    def _on_init(self):
        self.name = "日志记录"
        self.last_data = None
        self.last_content = None

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


class Neixin(Script):

    def _on_init(self):
        self.name = "内心找寻"
    
    def _on_not_battle(self):
        print("---------------------------------------")
        for unit in self.cg.map.units:
            print(f"{unit.name}:{unit.location}")
        time.sleep(2)
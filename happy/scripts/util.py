from happy.interface import Script
import logging


class Logger(Script):

    def _on_init(self):
        self.name = "日志记录"
        self.last_data = None
        self.last_content = None

    def _on_not_battle(self):

        pointer = self.cg.mem.read_int(0x0057A718)
        data = self.cg.mem.read_string(pointer,encoding="utf-8")
        content = self.cg.dialog.content

        if data and data!= last_data:
            logging.info(data.replace("\n",""))
            last_data = data
        
        if content and content!=last_content:
            logging.info(content.replace("\n",""))
            last_content = content

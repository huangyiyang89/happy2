import time
from happy.interface.mem import LocationBase
from happy.util import b62


class Dialog(LocationBase):

    @property
    def is_open(self):
        #self.mem.read_int(0x00C1D114) > 10 or 
        if self.type != -1:
            return True
        return False

    @property
    def type(self) -> int:
        """无对话框为-1"""
        return self.mem.read_int(0x005709B8)

    @property
    def model(self) -> int:
        # return self.mem.re    ad_int(0x00C32AAC)
        return self.mem.read_int(0x00C43900)

    @property
    def model_62(self) -> str:
        return b62(self.model)

    @property
    def selections(self):
        """type == 0 的选项列表"""
        flag = self.mem.read_int(0x00C762F4)
        list = []
        for i in range(16):
            value = 1
            if flag & value == 1:
                list.append(value << i)
            if flag == 0:
                break
            flag = flag >> 1
        return list

    @property
    def content(self) -> str:
        if self.is_open:
            content = ""
            for i in range(10):
                content += self.mem.read_string(0x00C32AB8 + i * 81, 81)
                content += "\n"
            return content
        return ""

    @property
    def is_doctor(self):
        if self.type == 19 and self.model == 336:
            return True
        return False

    @property
    def is_nurse(self):
        if self.type == 2 and self.model in (328, 364):
            return True
        return False

    @property
    def is_seller(self):
        """type == 5 and model == 333"""
        if self.type == 5 and self.model == 333:
            return True
        return False

    @property
    def seller_name(self) -> str:
        if self.is_seller:
            return self.mem.read_string(0x00C43BF4)
        return ""

    @property
    def npc_id(self) -> int:
        return self.mem.read_int(0x00CAF1F4)

    @property
    def npc_id_62(self) -> str:
        return b62(self.npc_id)

    @property
    def _unknown(self) -> int:
        return self.mem.read_int(0x00C32AB4)

    def reply(self, context: str = "", action: int | str = 0):
        """根据对话上下文，回复相应action,action为int表示第0,1,2个选项"""

        if not self.is_open:
            return
        if context not in self.content:
            return
        if isinstance(action, int):
            if action < len(self.selections):
                action = self.selections[action]
            action = b62(action)

        action = (
            f"xD {self._x_62} {self._y_62} {self.model_62} {self.npc_id_62} {action}"
        )
        self.mem.decode_send(action)
        time.sleep(1)

    def drop_ensure(self):
        if "確定丟棄" in self.content:
            self.mem.decode_send(f"xD {self._x_62} {self._y_62} {self.model_62} -1 1")
            self.close()

    def close(self):
        """能够关闭游戏中所有窗口"""
        self.mem.write_ushort(0x0072BD18, 2)
        self.mem.write_ushort(0x0072BD83, 4)
        time.sleep(0.1)

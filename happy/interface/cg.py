import time
import threading
import logging

from typing import Literal, Type
from pymem.exception import MemoryReadError

from .player import Player
from .pet import PetCollection
from .map import Map
from .mem import CgMem
from .dialog import Dialog
from .battle import Battle
from .item import ItemCollection
from .script import Script
from .team import Team

from happy.util import b62


class Cg:
    def __init__(self, cgmem: CgMem):
        self.mem = cgmem
        self._scripts: list[Script] = []
        self.player = Player(self.mem)
        self.map = Map(self.mem)
        self.dialog = Dialog(self.mem)
        self.battle = Battle(self.mem)
        self.items = ItemCollection(self.mem)
        self.pets = PetCollection(self.mem)
        self.team = Team(self.mem)

        self.__thread = threading.Thread(target=self._main_loop)
        self.stopped_callback = None

    
    def start_scripts_thread(self):
        self.__thread.start()

    @property
    def state(self):
        """输入账号界面=1 服务器选择=2 角色选择=3 角色创建=4 登陆中=6 游戏中=9 战斗中=10 掉线黑屏=11
        獵殺任務領取
        """
        return self.mem.read_int(0x00F62930)

    @property
    def state2(self):
        """输入账号界面=3  服务器选择=1 角色选择=11 游戏中=3 战斗输入指令中=4 等待战斗动画中=6   遇敌 5-1-2-3-4  退出战斗2-8-11-2-3"""
        return self.mem.read_int(0x00F62954)

    @property
    def account(self):
        return self.mem.read_string(0x00D15644)

    @property
    def is_moving(self) -> bool:
        return self.mem.read_int(0x0054DCB0) != 65535

    def _main_loop(self):
        while True:
            try:
                for script in self._scripts:
                    script.update()
            except MemoryReadError as e:
                print(e)
                break

        if self.stopped_callback is not None:
            self.stopped_callback(self)
        logging.warning(self.account, "线程退出")
        del self.mem
        del self

    def go_to(self, x: int | tuple, y: int = None):
        if y is None:
            x, y = x
        if self.map.location == (x, y):
            return

        # 走路
        # 0046845D  原A3 C8 C2 C0 00 改90 90 90 90 90
        # 00468476  原89 0D C4 C2 C0 00 改90 90 90 90 90 90
        # 00C0C2C4 X 00C0C2C8 Y 00C0C2DC 置1

        self.mem.write_bytes(0x0046845D, bytes.fromhex("90 90 90 90 90"), 5)
        self.mem.write_bytes(0x00468476, bytes.fromhex("90 90 90 90 90 90"), 6)
        self.mem.write_int(0x00C0C2C4, x)
        self.mem.write_int(0x00C0C2C8, y)
        self.mem.write_int(0x00C0C2DC, 1)
        time.sleep(0.1)

        # 还原
        self.mem.write_int(0x00C0C2DC, 0)
        self.mem.write_bytes(0x0046845D, bytes.fromhex("A3 C8 C2 C0 00"), 5)
        self.mem.write_bytes(0x00468476, bytes.fromhex("89 0D C4 C2 C0 00"), 6)

    def nav_to(self, x: int | tuple, y: int = None):
        if y is None:
            dest = x
        else:
            dest = (x, y)
        if self.map.location == dest:
            return True
        path = self.map.search(dest)
        if path:
            self.go_to(path[0])
            return True
        else:
            return False

    def nav_dungeon(self):
        transports = self.map.file.transports
        if len(transports) > 1:
            transports.sort(key=lambda x: x[2])
            logging.info(transports)
            if "地下" in self.map.name:
                transports.reverse()
            x, y, o = transports[0]
            self.nav_to(x, y)

    def click(self, direction: Literal["A", "B", "C", "D", "E", "F", "G", "H"]):
        """鼠标右键点击交互
        Args:
            direction: A-H,顺时针表示左上,上,右上,右,右下,下,左下,左
        """
        self.mem.decode_send(f"zA {self.map.x_62} {self.map.y_62} {direction} 0")

    def click_to(self, x: int | tuple, y: int = None):
        """如果距离足够，点击目标位置"""
        if y is None:
            x, y = x
        # 获取当前地图位置的x, y坐标
        current_x, current_y = self.map.location

        # 计算目标位置与当前位置的差值
        diff = (x - current_x, y - current_y)

        # 定义方向映射，根据坐标差值找到对应的方向
        directions = {
            (0, -1): "A",
            (0, -2): "A",
            (1, -1): "B",
            (2, -2): "B",
            (1, 0): "C",
            (2, 0): "C",
            (1, 1): "D",
            (2, 2): "D",
            (0, 1): "E",
            (0, 2): "E",
            (-1, 1): "F",
            (-2, 2): "F",
            (-1, 0): "G",
            (-2, 0): "G",
            (-1, -1): "H",
            (-2, -2): "H",
        }

        # 获取对应的方向
        direction = directions.get(diff)

        # 如果存在有效的方向，则执行点击操作
        if direction:
            self.click(direction)

    def dialogue_to(self, *coordinate):
        """如果没有对话框，click_to(x,y)"""
        if self.dialog.is_open:
            return
        # self.dialog.close()
        self.click_to(coordinate)
        time.sleep(0.5)

    @property
    def battle_speed(self):
        # default value is 16.6666666666666667
        value = self.mem.read_double(0x00548F10)
        return value

    @battle_speed.setter
    def battle_speed(self, value: int):
        if value:
            speed = 10.0 - value
        else:
            speed = 16.6666666666666667
        self.mem.write_double(0x00548F10, speed)

    @property
    def move_speed(self):
        value = self.mem.read_int(0x00F4C460)
        return value

    @move_speed.setter
    def move_speed(self, value: int):
        self.mem.write_int(0x00F4C460, value)

    def load_script(self, script: Script | Type[Script]):
        """加载脚本"""
        for loaded_script in self._scripts:
            if type(loaded_script) == type(script) or type(loaded_script) == script:
                return False
        if isinstance(script, Script):
            self._scripts.append(script)
            return True
        elif isinstance(script, type) and issubclass(script, Script):
            instance = script(self)
            self._scripts.append(instance)
            return True

    def request(
        self,
        action: str,
        dialog_model: int | str | None = None,
        npc_id: int | str | None = None,
    ):
        """
        仅传入action，只有打开了窗口才会行动
        """
        if dialog_model is None or npc_id is None:
            if not self.dialog.is_open:
                return
        if dialog_model is None:
            dialog_model = self.dialog.model
        if npc_id is None:
            npc_id = self.dialog.npc_id
        if isinstance(dialog_model, int):
            dialog_model = b62(dialog_model)
        if isinstance(npc_id, int):
            npc_id = b62(npc_id)
        self.mem.decode_send(
            f"xD {self.map.x_62} {self.map.y_62} {dialog_model} {npc_id} {action}"
        )

    def buy(self, item_index: int, amount: int = 1, seller_name=""):
        if self.dialog.is_seller and seller_name in self.dialog.seller_name:
            self.request(f"0 {item_index}\\\\z{amount}", 335)
            time.sleep(0.5)

    def reply(self, context: str = "", action: int | str = 0):
        """
        判断对话上下文，回复指令

        未打开对话框直接return
        """
        self.dialog.reply(context, action)

    def tp(self):
        self.mem.decode_send("lO")
        self.mem.write_int(0x00F62954, 7)
        self.mem.write_int(0x00F62954, 3)
        time.sleep(1)

    def hunt_message(self):
        text = self.mem.read_string(0x0019CBE0, 100)
        print(text)

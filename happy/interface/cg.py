import time
import threading
import logging
import random
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
from .window import Window

from happy.util import b62
from happy.util.captcha import solve_captcha


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
        self.window = Window(self.mem.process_id)
        self._last_map_id = 0
        self._thread = threading.Thread(target=self._main_loop)
        self.stopped_callback = None

    def start_scripts_thread(self):
        if not self._thread.is_alive():
            self._thread.start()

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
        return self.mem.read_string(0x00F66572)

    @account.setter
    def account(self, value):
        self.mem.write_string(0x00F66572, value)

    @property
    def password(self):
        return self.mem.read_string(0x00F6653F)

    @password.setter
    def password(self, value):
        self.mem.write_string(0x00F6653F, value)

    @property
    def is_moving(self) -> bool:
        return self.mem.read_int(0x0054DCB0) != 65535

    @property
    def stopped(self):
        if not hasattr(self, "mem"):
            return True
        return False

    def _main_loop(self):
        while True:
            try:
                for script in self._scripts:
                    script.update()
                time.sleep(0.1)
            except Exception as e:
                logging.warning(e)
                break
        if self.stopped_callback is not None:
            self.stopped_callback(self)
        logging.warning("线程结束============================================")
        del self.mem

    def go_to(self, x: int | tuple, y: int = None):
        """走路到坐标x,y
        return: 是否到达目的地, None表示未执行动作
        """
        if self.state != 9 or self.state2 != 3:
            return None

        if y is None:
            x, y = x
        if self.map.location == (x, y):
            return True

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
        """
        导航到坐标x,y
        return: 是否到达目的地, None表示无法到达
        """
        if self.state != 9 or self.state2 != 3:
            return False

        if y is None:
            dest = x
        else:
            dest = (x, y)

        # 已到达目的地返回True
        if self.map.location == dest:
            return True

        path = self.map.search(dest)
        if path:
            if self.team.is_leader and self.map.file.is_dungeon and len(path) == 1:
                time.sleep(0.5)

            self.go_to(path[0])
            return True

        return None

    def nav_dungeon(self, back=False):
        if self.state != 9 or self.state2 != 3:
            return False

        transports = self.map.find_transports()
        if len(transports) > 1:
            transports.sort(key=lambda x: x[2])
            if self.map.name == "佈滿青苔的洞窟1樓":
                transports.reverse()
            if "地下" in self.map.name:
                transports.reverse()
            if back:
                transports.reverse()
            x, y, o = transports[0]
            if self.map.location == (x, y):
                self.go_to(
                    self.map.x + random.randint(-1, 1),
                    self.map.y + random.randint(-1, 1),
                )
            self.nav_to(x, y)

    def click(self, direction: Literal["A", "B", "C", "D", "E", "F", "G", "H"]):
        """鼠标右键点击交互 Sleep 0.5s, A-H,表示左上,上,右上,右,右下,下,左下,左"""
        if self.state != 9 or self.state2 != 3:
            return False

        self.mem.decode_send(f"zA {self.map.x_62} {self.map.y_62} {direction} 0")
        time.sleep(1)

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
            return True

        return False

    def dialogue_to(self, *coordinate):
        """如果没有对话框，click_to(x,y)"""
        if self.state != 9 or self.state2 != 3:
            return False

        if self.dialog.is_open:
            return False
        # self.dialog.close()
        return self.click_to(coordinate)

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
            time.sleep(1)

    def say(self, content: str):
        self.mem.decode_send(f"uSr {self.map.x_62} {self.map.y_62} P|{content} 0 5 0")

    def reply(self, context: str = "", action: int | str = 0):
        """根据对话上下文，回复相应action,action为int表示第0,1,2个选项
        return: 是否成功回复"""

        if not self.dialog.is_open:
            return False
        if context not in self.dialog.content:
            return False
        if isinstance(action, int):
            if action < len(self.dialog.selections):
                action = self.dialog.selections[action]
            action = b62(action)

        action = (
            f"xD {self.map.x_62} {self.map.y_62} {self.dialog.model_62} {self.dialog.npc_id_62} {action}"
        )
        self.mem.decode_send(action)
        time.sleep(1)
        return True

    def tp(self):
        self.mem.decode_send("lO")
        time.sleep(1)
        if self.state == 10:
            self.mem.write_int(0x00F62954, 7)

    def find_script(self, name):
        for script in self._scripts:
            if script.name == name:
                return script
        return None

    def hunt_message(self):
        text = self.mem.read_string(0x0019CBE0, 100)
        print(text)

    def solve_if_captch(self):
        code = self.mem.read_string(0x00C32D4E, 10)
        if code != "" and code.isdigit() and len(code) == 10:
            version = self.mem.read_string(0x00C32CAC, 20)
            isv2 = "v2" in version
            if isv2:
                logging.warning("v2 capcha")
                # success = solve_captcha_v2(self.account, code)
            else:
                success = solve_captcha(self.account, code)
            if success:
                self.mem.write_string(0x00C32D4E, "\0\0\0\0\0\0\0\0\0\0")
            # else:
                # context = self.mem.read_string(0x00C32D40, 50)
                # logging.critical(
                #     "验证失败,账号:"
                #     + self.account
                #     + ",code:"
                #     + code
                #     + ",context:"
                #     + context
                # )

    def set_auto_login(self, enable=True):
        # set_auto_ret_blackscreen
        # 005122DB  黑屏跳出 0F 84 4D FF FF FF 改90 90 90 90 90 90
        if enable:
            self.mem.write_bytes(0x005122DB, bytes.fromhex("90 90 90 90 90 90"), 6)
        else:
            self.mem.write_bytes(0x005122DB, bytes.fromhex("0F 84 4D FF FF FF"), 6)

        # set_auto_select_charater
        # call start at 0045A285
        #                                                              0/1左侧右侧角色
        # 0045A2A0 原83 F8 06 0F 87 0D 04 00 00 改 B8 01 00 00 00 66 BB 01 00

        if enable:
            character = self.mem.read_int(0x00F627F8)
            if character == 0:
                self.mem.write_bytes(
                    0x0045A2A0, bytes.fromhex("B8 01 00 00 00 66 BB 00 00"), 9
                )
            else:
                self.mem.write_bytes(
                    0x0045A2A0, bytes.fromhex("B8 01 00 00 00 66 BB 01 00"), 9
                )
        else:
            self.mem.write_bytes(
                0x0045A2A0, bytes.fromhex("83 F8 06 0F 87 0D 04 00 00"), 9
            )

        # set_auto_login
        # 00458C40 函数开头
        # 写入几线
        # 00458E1A  E8 80 F0 FF FF 改 B8 D3 00 00 00 BE 03 00 00 00 90 过跳转

        # 处理重连失败弹窗
        # 00458CB9 39 35 54 29 F6 00 0F 85 69 02 00 00 改C7 05 54 29 F6 00 01 00 00 00 90 90

        if enable:
            line = self.mem.read_int(0x00927644)
            line_str = str(line).zfill(2)
            self.mem.write_bytes(
                0x00458E1A,
                bytes.fromhex(f"B8 D3 00 00 00 BE {line_str} 00 00 00 90"),
                11,
            )
        else:
            self.mem.write_bytes(
                0x00458E1A, bytes.fromhex("55 E8 80 F0 FF FF 83 C4 04 A8 40"), 11
            )

    def retry_if_login_failed(self):
        # 1没有小窗 3正在连接
        if self.state == 2 and self.state2 not in (1, 3):
            # state2 写1
            self.mem.write_int(0x00F62954, 1)
            time.sleep(3)

    def set_popup_explorer(self, enable=True):
        """禁止游戏弹出网页"""
        pointer = self.mem.read_int(0x0053E220)
        if enable:
            self.mem.write_bytes(pointer, bytes.fromhex("8B FF 55"), 3)
        else:
            self.mem.write_bytes(pointer, bytes.fromhex("C2 04 00"), 3)

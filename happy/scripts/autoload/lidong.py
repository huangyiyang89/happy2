import random
import time
import logging
from happy.interface import Script
from happy.interface.map import MapUnit


class Lidong(Script):
    def _on_init(self):
        self.name = "里洞魔石"
        self._sell_record = []
        self._move_record = [(0, 0, 0), (1, 1, 1), (2, 2, 2)]
        self.should_go_back = False

    def _on_start(self):
        self._sell_record = []
        self.cg.set_auto_login()
        self.cg.set_popup_explorer(False)

    def _on_stop(self):
        self.cg.set_auto_login(False)
        self.cg.set_popup_explorer(True)

    def _on_update(self):
        self.cg.solve_if_captch()
        self.cg.retry_if_login_failed()

        if self.cg.state == 10 and self.cg.state2 == 2 and self.cg.map.id == 30010:
            logging.warning(
                f"{self.cg.account} {self.cg.player.name} 回城卡死,{self.cg.map.name} {self.cg.map.x},{self.cg.map.y}"
            )
            self.cg.mem.write_int(0x00F62954, 7)
            time.sleep(1)

    def _on_not_moving(self):
        self._stuck_detect()
        if self.cg.map.name in ["亞諾曼城", "中央醫院"]:
            if self.cg.items.count > 10:
                self._go_to_sell()
                return
            if (
                self.cg.player.hp_per != 100
                or self.cg.player.mp_per != 100
                or not self.cg.pets.full_state
            ):
                self._go_to_heal()
                return

        if not self.cg.items.has_weapon:
            weapon = self.cg.items.find("弓")
            if weapon:
                self.cg.items.use(weapon)
            else:
                self._go_to_buy_weapon()
            return

        if not self.cg.items.crystal:
            crystal = self.cg.items.find("地水的水晶")
            if crystal:
                self.cg.items.use(crystal)
            else:
                self._go_to_buy_crystal()
            return

        if self.cg.items.count == 20:
            self._go_to_sell()
            return

        if (
            self.cg.player.hp_per < 30
            or self.cg.player.mp < 40
            or (self.cg.pets.on_battle and self.cg.pets.on_battle.hp_per < 30)
        ):
            self._go_to_heal()
            return

        if self.cg.player.injury > 0 or (
            self.cg.pets.on_battle and self.cg.pets.on_battle.injury > 0
        ):
            self._go_to_cure()
            return

        if (
            len(self.cg.player.customize_title) > 0
            and self.cg.player.customize_title in "012345"
        ):
            team_config = int(self.cg.player.customize_title)

            # 队员模式
            if team_config == 0 and self.cg.team.count == 0:
                self._go_to_W1()
                if self.cg.map.location == (68, 100):
                    self.cg.click("G")
                    self.cg.team.join()
                    time.sleep(1)
                return
            elif team_config == 0 and self.cg.team.count > 0:
                return

            # 队长模式
            if self.cg.team.count < team_config:
                self._go_to_W1()
                if self.cg.map.location == (68, 100):
                    self.cg.go_to(67, 100)
                return
            else:
                self._go_to_dungeon()

        else:
            self._go_to_dungeon()

    def _stuck_detect(self):
        if time.time() - self._move_record[2][0] >= 20:
            self._move_record.pop(0)
            self._move_record.append((time.time(), self.cg.map.x, self.cg.map.y))
        if (
            self._move_record[0][1:]
            == self._move_record[1][1:]
            == self._move_record[2][1:]
        ):
            logging.warning(
                f"{self.cg.account} {self.cg.player.name} 角色疑似卡死,{self.cg.map.name} {self.cg.map.x},{self.cg.map.y} TP. \n \
                last_map_id {self._last_map_id} , last_start {self.cg.map._last_start},last_dest {self.cg.map._last_dest} ,last_path {self.cg.map._last_searched_path} \n \
                "
            )
            
            self.cg.tp()
            self._move_record = [(0, 0, 0), (1, 1, 1), (2, 2, 2)]

    def _print_efficient_record(self):
        self._sell_record.append((time.time(), self.cg.items.gold))
        if len(self._sell_record) > 2:
            time_diff = self._sell_record[-1][0] - self._sell_record[1][0]
            gold_diff = self._sell_record[-1][1] - self._sell_record[1][1]
            eff = 3600 * gold_diff // time_diff
            logging.info(f"{self.cg.account} 效率: {eff}/h 当前：{self.cg.items.gold}")

    def _go_to_W1(self):
        if (
            self.cg.map.name == "亞諾曼城"
            and self.cg.map.x in [67, 68]
            and self.cg.map.y == 100
        ):
            return True
        if self.cg.map.name == "亞諾曼城" and (
            self.cg.map.location == (120, 139) or self.cg.map.location == (194, 93)
        ):
            self.cg.click("A")
        else:
            self.cg.tp()

    def _go_to_dungeon(self):

        if self.cg.map.name == "亞諾曼城":
            if self.cg.map.location == (120, 139) or self.cg.map.location == (194, 93):
                self.cg.click("A")

            elif self.cg.map.x < 80:
                self.cg.nav_to(21, 126)
            else:
                self.cg.tp()
            return

        if self.cg.map.name == "德威特島":
            self.cg.nav_to(129, 295)
            return

        if self.cg.map.name == "里歐波多洞窟":

            entrance = self.cg.map.units.find(
                name=" ", type=1, flag=4096, model_id_lt=103011
            )
            if isinstance(entrance, MapUnit):
                if self.cg.map.location == entrance.location:
                    self.cg.go_to(
                        self.cg.map.x + random.randint(-1, 1),
                        self.cg.map.y + random.randint(-1, 1),
                    )
                self.cg.nav_to(entrance.location)
            else:
                self.cg.nav_to(25, 19)
            return

        if "里歐波多洞窟地下14層" in self.cg.map.name:
            self.should_go_back = True
            self.cg.nav_dungeon(self.should_go_back)
            return
        
        if self.cg.map.name in ["里歐波多洞窟地下1層","里歐波多洞窟地下9層"]:
            # transport_positions = {(x, y) for x, y, _ in self.cg.map.find_transports()}
            # for _ in range(30):
            #     dest = (
            #         self.cg.map.x + random.randint(-1, 1),
            #         self.cg.map.y + random.randint(-1, 1),
            #     )
            #     if dest not in transport_positions and self.cg.map.file.check_flag(dest) and dest != self.cg.map.location:
            #         break
            # self.cg.go_to(dest)
            self.should_go_back = False
            self.cg.nav_dungeon(self.should_go_back)
            return

        
        if "里歐波多洞窟地下" in self.cg.map.name:
            self.cg.nav_dungeon(self.should_go_back)
            return

        self.cg.tp()

    def _go_to_sell(self):
        if self.cg.map.name != "亞諾曼城":
            self.cg.tp()
        self.cg.nav_to(132, 133)
        if self.cg.dialogue_to(133, 132):
            self._print_efficient_record()

    def _go_to_hospital(self):
        if self.cg.map.name == "亞諾曼城":
            self.cg.nav_to(116, 134)
        else:
            self.cg.tp()

    def _go_to_heal(self):
        if self.cg.map.name == "中央醫院":
            self.cg.nav_to(13, 23)
            self.cg.dialogue_to(14, 22)
        else:
            self._go_to_hospital()

    def _go_to_cure(self):
        if self.cg.map.name == "中央醫院":
            self.cg.nav_to(9, 7)
            if self.cg.dialogue_to(10, 6):
                logging.info(f"{self.cg.account} 受伤，已治疗。")
        else:
            self._go_to_hospital()

    def _go_to_buy_crystal(self):
        if self.cg.map.name == "亞諾曼城":
            self.cg.nav_to(97, 128)
        elif self.cg.map.name == "命運小屋":
            self.cg.nav_to(15, 22)
            self.cg.dialogue_to(17, 22)
            self.cg.buy(9)
        else:
            self.cg.tp()

    def _go_to_buy_weapon(self):
        if self.cg.map.name == "亞諾曼城":
            self.cg.nav_to(100, 114)
        elif self.cg.map.name == "銳健武器店":
            self.cg.nav_to(18, 13)
            self.cg.dialogue_to(20, 13)
            self.cg.buy(3)
        else:
            self.cg.tp()




import random
import time
import logging
from happy.interface import Script

class Yanhuang(Script):
    def _on_init(self):
        self.name = "炎黄洞窟"
        self._sell_record = []

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
    
    def _on_not_moving(self):
        if self.cg.map.name in ["法蘭城", "醫院"]:
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
            crystal = self.cg.items.find("火風的水晶")
            if crystal:
                self.cg.items.use(crystal)
            else:
                self._go_to_buy_crystal()
            return
        
        if (
            self.cg.player.hp_per < 30
            or (self.cg.player.hp_per < 50 and self.cg.player.mp < 40)
            or (self.cg.pets.on_battle and self.cg.pets.on_battle.hp_per < 30)
        ):
            self._go_to_heal()
            time.sleep(random.randint(1, 3))
            return

        if self.cg.player.injury > 0 or (
            self.cg.pets.on_battle and self.cg.pets.on_battle.injury > 0
        ):
            self._go_to_cure()
            return
        
        
        # 队长模式
        if (
            len(self.cg.player.customize_title) > 0
            and self.cg.player.customize_title in "12345"
        ):
            team_config = int(self.cg.player.customize_title)
            if self.cg.team.count < team_config:
                self._go_to_qili()
                if self.cg.map.location == (13, 9):
                    self.cg.go_to(13, 10)
                return
            else:
                self._go_to_dungeon()
        # 队員
        else:
            if self.cg.team.count == 0:
                self._go_to_qili()
                if self.cg.map.location == (13, 9):
                    self.cg.click("E")
                    self.cg.team.join()
                    time.sleep(1)
            return

    def _go_to_buy_weapon(self):
        if self.cg.map.name == "法蘭城" and self.cg.map.in_area(146,122,170,160):
            self.cg.go_to(151, 122)
            self.cg.dialogue_to(150, 122)
            self.cg.buy(3)
        else:
            self._go_to_next_transport()

    def _go_to_qili(self):
        if self.cg.map.name == "奇利村的傳送點":
            return True
        if self.cg.map.name == "啟程之間":
            self.cg.nav_to(9,33)
            self.cg.dialogue_to(8,32)
            self.cg.reply("這裡是往奇利村的傳送點")
            self.cg.reply("要使用嗎？")
        else:
            self._go_to_transfer_station()

    def _go_to_dungeon(self):
        if self.cg.map.name == "炎黃洞窟":
            if self.cg.map.in_area(25,6,40,11):
                self.cg.go_to(33+random.randint(-6,6), 8+random.randint(-2,2))
            else:
                self.cg.nav_to(33, 8)
        elif self.cg.map.name == "奇利村的傳送點":
            self.cg.go_to(7,6)
        elif self.cg.map.name == "村長的家" and self.cg.map.y<5:
            self.cg.go_to(7,1)
        elif self.cg.map.name == "村長的家" and self.cg.map.y>5:
            self.cg.go_to(1,8)
        elif self.cg.map.name == "奇利村":
            self.cg.nav_to(59, 45)
        elif self.cg.map.name == "索奇亞":
            self.cg.nav_to(267,253)


    def _print_efficient_record(self):
        self._sell_record.append((time.time(), self.cg.items.gold))
        if len(self._sell_record) > 2:
            time_diff = self._sell_record[-1][0] - self._sell_record[1][0]
            gold_diff = self._sell_record[-1][1] - self._sell_record[1][1]
            eff = 3600 * gold_diff // time_diff
            logging.info(f"{self.cg.account} 效率: {eff}/h 当前：{self.cg.items.gold}")
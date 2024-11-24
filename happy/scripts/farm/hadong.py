import random
import time
import logging
from happy.interface import Script

class Hadong(Script):
    def _on_init(self):
        self.name = "哈洞练级"

    def _on_start(self):
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
                or not self.cg.pets.full_state
            ):
                self._go_to_heal()
                return
            
        if not self.cg.items.has_weapon and self.cg.items.gold>=400:
            weapon = self.cg.items.find("弓")
            if weapon:
                self.cg.items.use(weapon)
            else:
                self._go_to_buy_weapon()
            return
        
        
        if (
            self.cg.player.hp_per < 30
            or (self.cg.pets.on_battle and self.cg.pets.on_battle.hp_per < 20)
        ):
            self._go_to_heal()
            time.sleep(random.randint(1, 5))
            return

        if self.cg.player.injury or (
            self.cg.pets.on_battle and self.cg.pets.on_battle.injury
        ):
            self._go_to_cure()
            return
        
        if not self.cg.pets.on_battle:
            first_pet = self.cg.pets.first
            if first_pet:
                first_pet.set_state(2)

        # 队长模式
        if (
            len(self.cg.player.customize_title) > 0
            and self.cg.player.customize_title in "12345"
        ):
            team_config = int(self.cg.player.customize_title)
            
            if self.cg.team.count < team_config:
                self._go_to_east_outside(True)
            else:
                self._go_to_dungeon()
        # 队員
        else:
            if self.cg.team.count == 0:
                self._go_to_east_outside()
                if self.cg.map.location == (475, 196):
                    self.cg.click("C")
                    self.cg.team.join()
                    time.sleep(1)

    def _go_to_east_outside(self,leader = False):
        if self.cg.map.name == "芙蕾雅" and self.cg.map.x<500:
            if leader:
                self.cg.go_to(476, 196)
            else:
                self.cg.go_to(475, 196)
            return
        if self.cg.map.name == "法蘭城" and self.cg.map.x > 200:
            self.cg.nav_to(281, 88)
        elif self.cg.map.name == "法蘭城" and self.cg.map.location == (72, 123):
            self.cg.click("C")
        elif self.cg.map.name == "法蘭城" and self.cg.map.location == (162, 130):
            self.cg.click("C")
        elif self.cg.map.name == "冒險者旅館 2樓" and self.cg.map.location == (12, 6):
            self.cg.click("A")   
        elif self.cg.map.name == "法蘭城" and self.cg.map.location == (141, 148):
            self.cg.click("A") 
        elif self.cg.map.name == "法蘭城" and self.cg.map.location == (63, 79):
            self.cg.click("A") 
        else:
            self.cg.tp()

    def _go_to_buy_weapon(self):
        if self.cg.map.name == "法蘭城" and self.cg.map.in_area(146,122,164,134):
            self.cg.go_to(151, 122)
            self.cg.dialogue_to(150, 122)
            self.cg.buy(3)
        else:
            self._go_to_S2()

    def _go_to_S2(self):
        if self.cg.map.name == "法蘭城" and self.cg.map.location == (162, 130):
            return True
        if self.cg.map.name == "法蘭城" and self.cg.map.location == (233, 78):
            self.cg.click("A")
        else:
            self.cg.tp()

    def _go_to_cure(self):
        if self.cg.map.name == "醫院":
            self.cg.nav_to(12, 19)
            if self.cg.dialogue_to(11, 18):
                logging.info(f"{self.cg.account} 受伤，已治疗。")
        else:
            self._go_to_hospital()

    def _go_to_dungeon(self):
        if self.cg.map.name == "芙蕾雅":
            self.cg.nav_to(672, 223)
        elif self.cg.map.name == "哈巴魯東邊洞穴 地下一樓":
            self.cg.go_to(12+random.randint(-3,3),41+random.randint(-3,3))

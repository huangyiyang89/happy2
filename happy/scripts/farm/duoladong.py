import logging
import time
import random
from happy.interface import Script


class Duoladong(Script):

    def _on_init(self):
        self.name = "多拉洞"

    def _on_start(self):
        self.cg.set_auto_login()
        self.cg.set_popup_explorer(False)
        self.should_go_back=False

    def _on_stop(self):
        self.cg.set_auto_login(False)
        self.cg.set_popup_explorer(True)

    def _on_update(self):
        self.cg.solve_if_captch()
        self.cg.retry_if_login_failed()
       

    @property
    def _should_sell(self):
        if self.cg.map.in_city:
            return self.cg.items.count > 10
        return self.cg.items.count == 20

    @property
    def _should_heal(self):
        if self.cg.map.in_city or self.cg.map.in_hospital:
            return (
                self.cg.player.hp_per != 100
                or self.cg.player.mp_per != 100
                or not self.cg.pets.full_state
            )
        return self.cg.player.hp_per < 30 or (
            self.cg.pets.on_battle and self.cg.pets.on_battle.hp_per < 30
        )

    @property
    def _should_buy_weapon(self):
        if not self.cg.items.has_weapon:
            weapon = self.cg.items.find("弓")
            if weapon:
                self.cg.items.use(weapon)
            else:
                return True
        return False

    @property
    def _should_buy_crystal(self):
        if not self.cg.items.crystal:
            crystal = self.cg.items.find("火風的水晶")
            if crystal:
                self.cg.items.use(crystal)
            else:
                return True
        return False

    @property
    def _should_cure(self):
        return self.cg.player.injury > 0 or (
            self.cg.pets.on_battle and self.cg.pets.on_battle.injury > 0
        )

    @property
    def _should_be_leader(self):
        return (
            len(self.cg.player.customize_title) > 0
            and self.cg.player.customize_title in "12345"
        )

    @property
    def _expected_team_count(self):
        return int(self.cg.player.customize_title)

    def _go_to_qishi(self):
        if self.cg.map.name == "起始之地":
            return True
        elif self.cg.map.id in [30010,1000]:
            self.cg.items.use("異界之匙")
            time.sleep(2)
            self.cg.reply("要使用異界的鑰匙")
        else:
            self.cg.tp()

    def _go_to_dungeon(self):
        if self.cg.map.name == "起始之地":
            self.cg.go_to(186, 99)
        elif self.cg.map.name == "普雷德島":
            self.cg.nav_to(563, 365)
        elif self.cg.map.name == "多拉洞":
            if self.should_go_back:
                self.cg.nav_to(27, 74)
                if self.cg.map.location == (27, 74):
                    self.should_go_back=False
            else:
                self.cg.nav_to(78, 29)
                if self.cg.map.location == (78, 29):
                    self.should_go_back=True

    def _on_not_moving(self):
        if self._should_sell:
            self._go_to_sell()
            return
        if self._should_heal:
            self._go_to_heal()
            return
        if self._should_buy_weapon:
            self._go_to_buy_weapon()
            return
        if self._should_buy_crystal:
            self._go_to_buy_crystal()
            return
        if self._should_cure:
            self._go_to_cure()
            return
        if self._should_be_leader:
            if self.cg.team.count < self._expected_team_count:
                self._go_to_qishi()
                if self.cg.map.in_area(98, 98, 5):
                    self.cg.go_to(97, 99)
                return
            else:
                self._go_to_dungeon()
        else:
            if self.cg.team.count == 0:
                self._go_to_qishi()
                if self.cg.map.in_area(98, 98, 5):
                    self.cg.go_to(98, 98)
                    self.cg.click("F")
                    self.cg.team.join()
                    time.sleep(1)

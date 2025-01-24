import random
import time
import logging
from happy.interface import Script
from happy.interface.map import MapUnit


class Level1to20(Script):
    def _on_init(self):
        self.name = "升级1-20"

    def _on_start(self):
        self.cg.set_auto_login()
        self.cg.set_popup_explorer(False)

    def _on_stop(self):
        self.cg.set_auto_login(False)
        self.cg.set_popup_explorer(True)

    def _on_update(self):
        self.cg.retry_if_login_failed()

    @property
    def _should_sell(self):
        if self.cg.items.count == 20:
            return True
        if self.cg.map.in_city and self.cg.items.count > 10:
            return True
        return False

    @property
    def _should_heal(self):
        if (self.cg.map.in_city or self.cg.map.in_hospital) and (self.cg.player.hp_per < 98 or not self.cg.pets.full_health):
            return True
        if self.cg.player.hp_per < 30:
            return True
        if self.cg.team.count == 0 and self.cg.player.mp < 40:
            return True
        if self.cg.pets.on_battle and self.cg.pets.on_battle.hp_per < 30:
            return True
        return False

    @property
    def _should_buy_weapon(self):
        if self.cg.items.right_hand is None and self.cg.items.left_hand is None:
            weapon = self.cg.items.find("弓")
            if weapon:
                self.cg.items.use(weapon)
                return False
            if self.cg.items.gold >= 600 and self.cg.player.level >= 10:
                return True
        return False

    def _on_not_moving(self):

        if not self.cg.pets.on_battle:
            first_pet = self.cg.pets.first
            if first_pet:
                first_pet.set_state(2)

        if self._should_sell:
            self._go_to_sell()
            return
        if self._should_heal:
            self._go_to_heal()
            return
        if self._should_cure:
            self._go_to_cure()
            return

        if self._should_buy_weapon:
            self._go_to_buy_weapon()
            return

        if self._should_buy_crystal:
            self._go_to_buy_crystal()
            return

        if self._should_be_leader:
            if self._should_go:
                self._go_to_dungeon()
            else:
                self._go_to_assemble()
            return

        if not self._should_be_leader and self.cg.team.count == 0:
            self._go_to_assemble()
            return

    def _go_to_assemble(self):
        if self.cg.map.id == 30010 and self.cg.map.within(68, 100, 10):
            if self._should_be_leader:
                self.cg.nav_to(69, 100)
            else:
                self.cg.nav_to(68, 100)
                self.cg.click_to(69, 100)
                self.cg.team.join()
        else:
            self._go_to_next_transport()

    def _go_to_dungeon(self):

        if self.cg.map.id == 30010:
            if self.cg.map.location == (120, 139) or self.cg.map.location == (194, 93):
                self.cg.click("A")
            elif self.cg.map.x < 80:
                self.cg.nav_to(21, 126)
            else:
                self.cg.tp()
            return

        if self.cg.map.name == "德威特島":
            if self.cg.player.level < 10:
                self.cg.go_to(183 + random.randint(-1, 1), 373 + random.randint(-1, 1))
                return
            else:
                if self.cg.map.within(291, 446, 20):
                    self.cg.nav_to(312, 452)
                if self.cg.map.within(400, 540, 6):
                    self.cg.go_to(
                        400 + random.randint(-5, 5), 540 + random.randint(-5, 5)
                    )
                else:
                    self.cg.nav_to(400, 540)
                return

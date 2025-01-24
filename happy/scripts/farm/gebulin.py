from happy.interface import Script
from happy.util import b62


class Gebulin(Script):
    def _on_init(self):
        self.name = "刷哥布林"
        self.should_open_dialog = True

    def _on_start(self):
        self._sell_record = []
        self.cg.set_auto_login()
        self.cg.set_popup_explorer(False)
        if not self.cg.pets.on_battle:
            pet = self.cg.pets.first
            if pet:
                pet.set_state(2)

    def _on_stop(self):
        self.cg.set_auto_login(False)
        self.cg.set_popup_explorer(True)

    def _on_update(self):
        self.cg.retry_if_login_failed()

    @property
    def _should_heal(self):
        return self.cg.player.hp_per < 20 or self.cg.player.hp < 70 or (self.cg.pets.on_battle and self.cg.pets.on_battle.hp_per < 20)

    @property
    def _should_sell(self):
        return self.cg.items.count >= 20 or self.cg.player.level >= 7

    def _go_to_sell(self):
        # 武器商人
        if self.cg.map.id == 1000 and self.cg.map.within(135, 120, 167, 158):
            self.cg.go_to(150, 123)
            self.cg.dialogue_to(150, 122)
        else:
            self._go_to_next_transport()

    def _on_not_moving(self):

        if self.cg.items.right_hand is None and self.cg.items.left_hand is None:
            self.cg.items.use("弓")
        if self._should_sell:
            self._go_to_sell()
        elif self._should_heal:
            self._go_to_heal()
        elif self._should_cure:
            self._go_to_cure()
        elif self._should_buy_weapon and self.cg.items.gold >= 400:
            self._go_to_buy_weapon()
        elif self.cg.map.id == 1000 and self.cg.map.within(130, 120, 180, 242):
            self.should_open_dialog = True
            self.cg.nav_to(153, 241)
        elif self.cg.map.id == 100:
            unit = self.cg.map.units.find_npc("哥布林士官")
            if self.cg.map.location == (437, 265) and unit:
                if self.cg.dialog.is_open:
                    self.cg.go_to(436, 265)
                    return
                self.cg.mem.decode_send(f"xD {b62(437)} {b62(265)} 5g {b62(unit.id)} 4")
                return
            if self.cg.map.location == (436, 265) and unit:
                self.cg.mem.decode_send(f"zA {b62(436)} {b62(265)} 6 0")
                self.cg.mem.decode_send(f"xD {b62(437)} {b62(265)} 5g {b62(unit.id)} 4")
                return
            else:
                self.cg.go_to(436, 265)

        else:
            self._go_to_next_transport()

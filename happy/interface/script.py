import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from happy.interface import Cg


class Script:

    def __init__(self, cg: "Cg") -> None:
        self.name = "noname script"
        self.cg = cg
        self.enable = False
        self._start_has_run = False
        self._stop_has_run = False
        self._last_map_id = 0
        self._last_location = (0, 0)
        self._stuck_counter = 0
        self._start_time = 0
        self._start_gold = 0
        self._on_init()

    def update(self):

        if not self.enable:
            if not self._stop_has_run:
                self._on_stop()
                self._stop_has_run = True
                self._start_has_run = False
            return

        if not self._start_has_run:
            self._on_start()
            self._start_time = time.time()
            self._start_gold = self.cg.items.gold
            self._start_has_run = True
            self._stop_has_run = False

        self._on_update()

        if self.cg.state == 9 and self.cg.state2 == 3:
            self._on_not_battle()
            if self.cg.map.id != self._last_map_id:
                self._on_map_changed()
                self._last_map_id = self.cg.map.id

            if self.cg.dialog.is_open:
                self._on_dialog()
            if self.cg.is_moving:
                self._on_moving()
            else:
                self._on_not_moving()
                if self._last_location == self.cg.map.location:
                    self._stuck_counter += 1
                    if self._stuck_counter >= 100:
                        self._on_move_stuck()
                else:
                    self._stuck_counter = 0

        if self.cg.battle.is_battling:
            self._on_battle()

    def _on_init(self):
        pass

    def _on_update(self):
        pass

    def _on_start(self):
        pass

    def _on_stop(self):
        pass

    def _on_battle(self):
        pass

    def _on_not_battle(self):
        pass

    def _on_moving(self):
        pass

    def _on_not_moving(self):
        pass

    def _on_map_changed(self):
        pass

    def _on_dialog(self):
        pass

    def _on_move_stuck(self):
        pass

    
    @property
    def _expected_team_count(self):
        try:
            count = int(self.cg.player.customize_title) 
        except:
            count = 0
        return count
    
    @property
    def _should_be_leader(self):
        return (
            len(self.cg.player.customize_title) > 0
            and self.cg.player.customize_title in "12345"
        )

    @property
    def _should_go(self):
        return (
            self._expected_team_count == self.cg.team.count and self.cg.team.is_leader
        )

    @property
    def _should_buy_weapon(self):
        if not self.cg.items.left_hand and not self.cg.items.right_hand:
            return True
        return False

    @property
    def _should_buy_crystal(self):
        if not self.cg.items.crystal:
            crystal = self.cg.items.find("水晶")
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
        

    def _go_to_sell(self):
        should_sell_special = False
        if (self.cg.items.find("紅頭盔") or self.cg.items.find("綠頭盔")) and self.cg.map.id == 1000:
            should_sell_special = True

        # 亚诺曼
        if self.cg.map.id == 30010 and self.cg.map.within(132, 133, 50) and not should_sell_special:
            self.cg.nav_to(132, 133)
            self.cg.dialogue_to(133, 132)
        # 东医老鼠
        elif self.cg.map.id == 1000 and self.cg.map.within(220, 60, 250, 110) and not should_sell_special:
            self.cg.nav_to(233, 83)
            self.cg.dialogue_to(232, 83)
        # 武器商人
        elif self.cg.map.id == 1000 and self.cg.map.within(135, 120, 167, 158) and should_sell_special:
            self.cg.nav_to(150, 123)
            self.cg.dialogue_to(150, 122)
        # 西医老鼠
        elif self.cg.map.id == 1000 and self.cg.map.within(60, 75, 85, 90) and not should_sell_special:
            self.cg.nav_to(73, 83)
            self.cg.dialogue_to(74, 83)
        else:
            self._go_to_next_transport()

    def _go_to_heal(self):
        # 东医
        if self.cg.map.id == 1112:
            self.cg.nav_to(7, 34)
            self.cg.dialogue_to(7, 33)
        # 西医
        elif self.cg.map.id == 1111:
            self.cg.nav_to(8, 33)
            self.cg.dialogue_to(8, 32)
        # 亚诺曼医院
        elif self.cg.map.id == 30105:
            self.cg.nav_to(13, 23)
            self.cg.dialogue_to(14, 22)
        else:
            self._go_to_hospital()

    def _go_to_hospital(self):
        # 去东医
        if self.cg.map.id == 1000 and self.cg.map.within(210, 60, 238, 87):
            self.cg.nav_to(221, 83)
        # 去西医
        elif self.cg.map.id == 1000 and self.cg.map.within(60, 70, 90, 120):
            self.cg.nav_to(82, 83)
        # 亚诺曼城
        elif self.cg.map.id == 30010 and self.cg.map.within(100, 120, 140, 150):
            self.cg.nav_to(116, 134)
        else:
            self._go_to_next_transport()

    def _go_to_cure(self):
        # 东医
        if self.cg.map.id == 1112:
            self.cg.nav_to(12, 19)
            self.cg.dialogue_to(11, 18)
        # 西医
        elif self.cg.map.id == 1111:
            self.cg.nav_to(10, 18)
            self.cg.dialogue_to(10, 17)
        # 亚诺曼医院
        elif self.cg.map.id == 30105:
            self.cg.nav_to(9, 7)
            self.cg.dialogue_to(10, 6)
        else:
            self._go_to_hospital()

    def _go_to_buy_crystal(self):
        if self.cg.map.name == "法蘭城" and self.cg.map.x < 100:
            self.cg.nav_to(94, 78)
        elif self.cg.map.name == "達美姊妹的店":
            self.cg.nav_to(17, 18)
            self.cg.dialogue_to(19, 18)
            self.cg.buy(11)
        elif self.cg.map.name == "亞諾曼城":
            self.cg.nav_to(97, 128)
        elif self.cg.map.name == "命運小屋":
            self.cg.nav_to(15, 22)
            self.cg.dialogue_to(17, 22)
            self.cg.buy(9)
        else:
            self._go_to_transfer_station()

    def _go_to_transfer_station(self):
        if self.cg.map.name == "啟程之間":
            return True
        if self.cg.map.name == "法蘭城" and self.cg.map.within(130, 100, 170, 160):
            self.cg.nav_to(153, 100)
        elif self.cg.map.name == "里謝里雅堡":
            self.cg.go_to(41, 50)
        elif self.cg.map.name == "里謝里雅堡 1樓":
            self.cg.nav_to(45, 20)
        else:
            self._go_to_next_transport()

    def _go_to_next_transport(self):
        # E1
        if self.cg.map.id == 1000 and self.cg.map.location == (242, 100):
            self.cg.click("C")
        # E2
        elif self.cg.map.id == 1000 and self.cg.map.location == (233, 78):
            self.cg.click("A")
        # S1
        elif self.cg.map.id == 1000 and self.cg.map.location == (141, 148):
            self.cg.click("A")
        # S2
        elif self.cg.map.id == 1000 and self.cg.map.location == (162, 130):
            self.cg.click("C")
        # W1
        elif self.cg.map.id == 1000 and self.cg.map.location == (63, 79):
            self.cg.click("A")
        # W2
        elif self.cg.map.id == 1000 and self.cg.map.location == (72, 123):
            self.cg.click("C")
        # 冒险者旅馆
        elif self.cg.map.id == 1164 and self.cg.map.location == (12, 6):
            self.cg.click("A")
        elif self.cg.map.id == 1000 and self.cg.map.within(225, 64, 240, 85):
            self.cg.nav_to(233, 78)
        elif self.cg.map.id == 30010 and self.cg.map.location in [
            (68, 100),
            (194, 93),
            (120, 139),
        ]:
            self.cg.click("A")
        else:
            self.cg.tp()

    def _go_to_buy_weapon(self, index=3):
        if index == 3:
            gong = self.cg.items.find("弓")
            if gong:
                self.cg.items.use(gong)
                return
        elif index == 5:
            xiaodao = self.cg.items.find("小刀")
            if xiaodao:
                self.cg.items.use(xiaodao)
                return

        if self.cg.map.name == "法蘭城" and self.cg.map.within(130, 122, 170, 160):
            self.cg.go_to(151, 122)
            self.cg.dialogue_to(150, 122)
            self.cg.buy(index)
        elif self.cg.map.name == "亞諾曼城":
            self.cg.nav_to(100, 114)
        elif self.cg.map.name == "銳健武器店":
            self.cg.nav_to(18, 13)
            self.cg.dialogue_to(20, 13)
            self.cg.buy(index)
        else:
            self._go_to_next_transport()

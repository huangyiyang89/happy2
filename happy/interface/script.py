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
                        if self.cg.state == 10 and self.cg.state2 == 2 and self.cg.map.id in [30010,1000]:
                            self.cg.mem.write_int(0x00F62954, 7)
                            time.sleep(1)
                        else:
                            self._on_stuck()
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

    def _on_stuck(self):
        pass

    @property
    def efficiency(self):
        if self._start_time == 0:
            return 0

        time_cost = time.time() - self._start_time
        gold_earned = self.cg.items.gold - self._start_gold
        if time_cost > 0:
            return gold_earned / time_cost * 3600
        return 0
    
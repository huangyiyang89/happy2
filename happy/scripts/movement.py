import logging
from happy.interface import Script


class AutoMaze(Script):
    def _on_init(self):
        self.name = "迷宫寻路"

    def _on_not_battle(self):
        self.cg.nav_dungeon()


class FaLanLogin(Script):
    def _on_init(self):
        return super()._on_init()

    def _on_not_battle(self):
        if self.cg.map.id == 1000:

            # E2
            if self.cg.map.location == (233, 78):
                self.cg.click("A")
            # S2
            if self.cg.map.location == (162, 130):
                self.cg.click("C")
            # W2
            if self.cg.map.location == (72, 123):
                self.cg.click("C")

            # E1
            if self.cg.map.location == (242, 100):
                self.cg.click("C")
            # S1
            if self.cg.map.location == (141, 148):
                self.cg.click("A")
            # W1
            if self.cg.map.location == (63, 79):
                self.cg.click("A")

        if self.cg.map.id == 1164 and self.cg.map.location == (12, 6):
            self.cg.click("A")

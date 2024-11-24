import random
from happy.interface import Script
from happy.interface.map import MapUnit

class Encounter(Script):

    def _on_init(self):
        self.name = "自动遇敌"
        self.range = 2
        self.start_x = 0
        self.start_y = 0
        self.stop_flag = False

    def _on_not_battle(self):
        if self.stop_flag:
            return

        if self.cg.map.x == 134 and self.cg.map.y == 174:
            self.cg.go_to(135, 175)
            return
        if self.cg.map.x == 135 and self.cg.map.y == 175:
            self.cg.go_to(134, 174)
            return

        if self.start_x == 0 and self.start_y == 0:
            self.start_x = self.cg.map.x
            self.start_y = self.cg.map.y

        if self.cg.map.x == self.start_x and self.cg.map.y == self.start_y:
            # 生成随机数 x
            x = random.choice([2, -2, 0, 0])
            # 根据 x 的值确定 y 的值
            if x in [-2, 2]:
                y = 0
            else:
                y = random.choice([2, -2])
            self.cg.go_to(
                self.start_x + x,
                self.start_y + y,
            )
        else:
            self.cg.go_to(self.start_x, self.start_y)

    def _on_battle(self):
        for friend in self.cg.battle.units.friends:
            if friend.hp < 2:
                self.stop_flag = True
                break

    def _on_start(self):
        self.start_x = 0
        self.start_y = 0
        self.stop_flag = False
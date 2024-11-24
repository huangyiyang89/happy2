from happy.interface import Script
import logging


class SpeedBattle(Script):

    def _on_init(self):
        self.name = "高速战斗"
        self.enable = True
        self.speed = 7

    def _on_not_battle(self):
        self.cg.battle_speed = 0

    def _on_update(self):
        if self.cg.state in (9, 10) and self.cg.state2 in (5, 1, 2, 4, 6, 11):
            player = self.cg.battle.player
            if player and (player.is_uncontrolled or player.hp == 0) and self.cg.battle.is_waiting_anime:
                logging.debug("玩家受控或死亡，停止高速战斗！")
                logging.debug(player._data_list)
                self.cg.battle_speed = 0
            else:
                self.cg.battle_speed = self.speed

    def _on_stop(self):
        self.cg.battle_speed = 0

class SpeedMove(Script):

    def _on_init(self):
        self.name = "高速移动"
        self.speed = 115
        self.enable = True

    def _on_not_battle(self):
        self.cg.move_speed = self.speed

    def _on_stop(self):
        self.cg.move_speed = 100
from happy.interface import Script
import time
import logging
class Assistant(Script):
    """自动补给，自动卖东西"""

    def _on_init(self):
        self.name = "智能助手"
        self.enable = True
        self.seller_list = [
            "水藍販售商",
            "平民防具販售處",
            "平民武器販售處",
            "旅行商人貝萊奇",
        ]

    def _auto_cure(self):
        if self.cg.dialog.is_doctor:
            self.cg.request("0 7")
            self.cg.dialog.close()

    def _auto_heal(self):
        if not self.cg.dialog.is_nurse:
            return
        if (
            self.cg.pets.full_state
            and self.cg.player.hp_per == 100
            and self.cg.player.mp_per == 100
        ):
            return
        model = self.cg.dialog.model
        if self.cg.player.mp_per < 100:
            self.cg.request("4", model + 1)
        if self.cg.player.hp_per < 100:
            self.cg.request("4", model + 3)
        if not self.cg.pets.full_state:
            self.cg.request("4", model + 4)
        time.sleep(0.5)

    def _auto_sell(self):

        if self.cg.dialog.seller_name not in self.seller_list:
            return

        items_str = ""
        for item in self.cg.items:
            if (
                "魔石" in item.name
                or "卡片" in item.name
                or ("寵物鈴鐺" in item.name and item.count >= 40)
                or ("紙人娃娃" in item.name and item.count >= 40)
            ):
                count = 1 if "寵物鈴鐺" in item.name else item.count
                count = 1 if "紙人娃娃" in item.name else count
                items_str += str(item.index) + r"\\z" + str(count) + r"\\z"
        if items_str != "":
            self.cg.request("0 "+items_str[:-3], "5o")
            time.sleep(0.5)

    def _on_dialog(self):
        self._auto_heal()
        self._auto_sell()
        self._auto_cure()


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
            if player and (player.is_uncontrolled or player.hp==0):

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
        self.speed = 125
        self.enable = True

    def _on_not_battle(self):
        self.cg.move_speed = self.speed

    def _on_stop(self):
        self.cg.move_speed = 100




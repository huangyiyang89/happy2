from happy.interface import Script
import time
import logging


class Assistant(Script):
    """自动补给，自动卖东西，自动吃喝"""

    def _on_init(self):
        self.name = "智能助手"
        self.enable = True
        self.seller_list = [
            "水藍販售商",
            "平民防具販售處",
            "平民武器販售處",
            "旅行商人貝萊奇",
        ]
        self.sell_record = []
        self._eat_food_flag = 0

    def _on_update(self):
        self.cg.solve_if_captch()

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

        if self.cg.player.mp_per < 100 and self.cg.player.job_name != "遊民":
            self.cg.request("4", model + 1)
        if self.cg.player.hp_per < 100:
            self.cg.request("4", model + 3)
        if not self.cg.pets.full_state:
            self.cg.request("4", model + 4)
        time.sleep(1)

    def _auto_sell(self):

        if self.cg.dialog.seller_name not in self.seller_list:
            return

        items_str = ""
        for item in self.cg.items:
            is_stacked_item = (
                True if item.name in ["寵物鈴鐺", "紙人娃娃", "斑駁的化石"] and item.count>=40 else False
            )
            if "魔石" in item.name or "卡片" in item.name or "綠頭盔" in item.name or "紅頭盔" in item.name or is_stacked_item:
                count = item.count // 40 if is_stacked_item else item.count
                items_str += str(item.index) + r"\\z" + str(count) + r"\\z"
        if items_str != "":
            self.cg.request("0 " + items_str[:-3], "5o")
            time.sleep(1)
            self.sell_record.append((time.time(), self.cg.items.gold))
            if len(self.sell_record) >= 3:
                time_span = self.sell_record[-1][0] - self.sell_record[1][0]
                gold_diff = self.sell_record[-1][1] - self.sell_record[1][1]
                speed = gold_diff * 3600 // time_span

                logging.info(
                    f"{self.cg.account} {time_span//60}分钟 {gold_diff}金币 {speed}/h"
                )

    def _auto_food(self):

        if self.cg.battle.is_battling:
            self._eat_food_flag = 0
            return

        if self._eat_food_flag == 0 and self.cg.map.name not in ["亞諾曼城", "法蘭城"]:
            food = self.cg.items.first_food
            if food and food.food_restore <= self.cg.player.mp_lost + 50:
                self.cg.items.use(food)
                self.cg.mem.decode_send("mjCv 0")
                self.cg.mem.decode_send(
                    f"iVfo {self.cg.map.x_62} {self.cg.map.y_62} {food.index_62} 0"
                )
                self._eat_food_flag = 1

    def _solve_tp_stuck(self):
        if (
            self.cg.state == 10
            and self.cg.state2 == 2
            and self.cg.map.id in [1000, 30010, 1164]
        ):
            self.cg.mem.write_int(0x00F62954, 7)
            time.sleep(1)

    def _on_dialog(self):
        self._auto_heal()
        self._auto_sell()
        self._auto_cure()

    def _on_battle(self):
        self._eat_food_flag = 0

    def _on_not_battle(self):
        self._auto_food()

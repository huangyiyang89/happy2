import random
import time
import logging
from happy.interface import Script
from happy.interface.map import MapUnit


class LevelUp(Script):

    def _on_init(self):
        self.name = "升级助手"
        if self.cg.player.level < 50:
            self.enable = True

    def _on_not_battle(self):
        if self.cg.player.remain_points > 0:
            lvl = self.cg.player.level
            if self.cg.player.strength_points < 250:
                self.cg.player.add_point(1)
                self.cg.player.add_point(1)
            if self.cg.player.defense_points < lvl:
                self.cg.player.add_point(2)
            if self.cg.player.agility_points < lvl + 15:
                self.cg.player.add_point(3)
            # if self.cg.player.endurance_points < lvl:
            #     self.cg.player.add_point(0)
            # if self.cg.player.level > 40 and self.cg.player.magical_points < 0:
            #     self.cg.player.add_point(4)
        if self.cg.pets.on_battle and self.cg.pets.on_battle.remain_points > 0:
            pet = self.cg.pets.on_battle
            if pet.name in ["改造樹精"]:
                pet.add_point(0)
            if pet.name in ["小蝙蝠", "使魔", "影蝙蝠", "異化強盾","覺醒的影蝙蝠"]:
                pet.add_point(1)

        if self.cg.player.job_name == "見習弓箭手":
            if not self.cg.dialog.is_open:
                self.cg.items.use("初心者背包")
                self.cg.items.drop("弓箭手推薦信")

            if self.cg.dialog.is_open:
                self.cg.reply()

            for item in self.cg.items.bags:
                if "訓練用" in item.name:
                    self.cg.items.use(item)

        if (
            self.cg.map.name == "國營第24坑道 地下1樓"
            and self.cg.items.find("試煉洞穴通行證")
            and self.cg.team.count == 0
        ):
            self.cg.dialogue_to(9, 14)
            self.cg.request("1")

        self.cg.items.use("大女神蘋果")

        if not self.cg.dialog.is_open:
            self.cg.items.drop("國民袍", "國民靴", "給勇者的信", "紅色花粉","車站一天票(時限)")
            #, "卡片？"

        if 25 > self.cg.player.level >= 5:
            self.cg.items.use("新手援助禮包LV5")
            self.cg.dialog.reply("確定要開啟禮包嗎", "4")

        if self.cg.player.level >= 25:
            self.cg.items.use("新手援助禮包LV25")
            self.cg.dialog.reply("確定要開啟禮包嗎", "4")

        self.cg.dialog.drop_ensure()

    def _on_not_moving(self):

        huoba = self.cg.items.find("火把")

        # 維諾亞村 - 打樹精
        if self.cg.map.name == "芙蕾雅" and huoba is not None:
            if self.cg.map.y > 345:
                self.cg.nav_to(380, 353)

        if self.cg.map.name == "醫院" and huoba is None:
            self.cg.dialogue_to(6, 5)
            self.cg.reply("願意聽聽嗎")
            self.cg.reply("前天有人拜託我去趕走兇暴的魔族")

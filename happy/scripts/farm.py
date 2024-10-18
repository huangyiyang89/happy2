import random
import time
import logging
from happy.interface import Script
from happy.interface.map import MapUnit


class AutoEncounter(Script):

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


class LevelUp(Script):

    def _on_init(self):
        self.name = "升级助手"

    def _on_not_battle(self):
        if self.cg.player.remain_points > 0:
            lvl = self.cg.player.level
            if self.cg.player.strength_points < 125:
                self.cg.player.add_point(1)
                self.cg.player.add_point(1)
            if self.cg.player.endurance_points < lvl:
                self.cg.player.add_point(0)
            if self.cg.player.agility_points < lvl:
                self.cg.player.add_point(3)
            if self.cg.player.defense_points < 0:
                self.cg.player.add_point(2)
            if self.cg.player.level > 40 and self.cg.player.magical_points < 0:
                self.cg.player.add_point(4)
        if self.cg.pets.on_battle and self.cg.pets.on_battle.remain_points > 0:
            pet = self.cg.pets.on_battle
            if pet.name in ["改造樹精"]:
                pet.add_point(0)
            if pet.name in ["小蝙蝠", "使魔", "影蝙蝠","異化強盾"]:
                pet.add_point(1)

        if self.cg.player.job_name == "見習弓箭手" and self.cg.map.name == "弓箭手公會":
            if not self.cg.dialog.is_open:
                self.cg.items.use("初心者背包")
                self.cg.items.drop("弓箭手推薦信")

            if self.cg.dialog.is_open:
                self.cg.reply()

            for item in self.cg.items.bags:
                if "訓練用" in item.name:
                    self.cg.items.use(item)

        if self.cg.map.name == "醫院" and self.cg.items.find("止痛藥") is None:
            self.cg.dialogue_to(16, 35)
            self.cg.buy(1)

        if (
            self.cg.map.name == "職業公會"
            and self.cg.map.x == 8
            and self.cg.map.y == 6
            and self.cg.items.find("止痛藥")
        ):
            self.cg.dialogue_to(10, 6)
            self.cg.request("4")

        if (
            self.cg.map.name == "國營第24坑道 地下1樓"
            and self.cg.items.find("試煉洞穴通行證")
            and self.cg.team.count == 0
        ):
            self.cg.dialogue_to(9, 14)
            self.cg.request("1")

        self.cg.items.use("大女神蘋果")

        if not self.cg.dialog.is_open:
            self.cg.items.drop("國民袍", "國民靴", "卡片？")

        if self.cg.player.level >= 5:
            self.cg.items.use("新手援助禮包LV5")
            self.cg.dialog.reply("確定要開啟禮包嗎", "4")

        self.cg.dialog.drop_ensure()

    def _on_not_moving(self):
        if self.cg.team.is_leader and self.cg.team.count == 5:
            if self.cg.map.name == "國營第24坑道 地下1樓":
                self.cg.nav_to(9, 5)
            if self.cg.map.name == "試煉之洞窟 第1層":
                self.cg.nav_to(33, 31)
            if self.cg.map.name == "試煉之洞窟 第2層":
                self.cg.nav_to(7, 9)
            if self.cg.map.name == "試煉之洞窟 第3層":
                self.cg.nav_to(42, 34)
            if self.cg.map.name == "試煉之洞窟 第4層":
                self.cg.nav_to(27, 12)
            if self.cg.map.name == "試煉之洞窟 第5層":
                self.cg.nav_to(39, 36)
            if self.cg.map.name == "試煉之洞窟 大廳":
                self.cg.nav_to(23, 17)

            # 西門-熊洞
            if self.cg.map.name == "芙蕾雅":
                if self.cg.map.y > 258 and self.cg.map.y < 317:
                    self.cg.nav_to(472, 316)

            # 熊洞
            if self.cg.map.name == "維諾亞洞穴 地下1樓":
                self.cg.nav_to(20, 59)
            if self.cg.map.name == "維諾亞洞穴 地下2樓":
                self.cg.nav_to(24, 81)
            if self.cg.map.name == "維諾亞洞穴 地下3樓":
                self.cg.nav_to(26, 64)

            # 熊洞-維諾亞村
            if self.cg.map.name == "芙蕾雅":
                if self.cg.map.y > 345:
                    self.cg.nav_to(331, 480)

            # 過海
            if self.cg.map.name == "索奇亞海底洞窟 地下1樓" and self.cg.map.id == 15005:
                self.cg.nav_to(18, 34)
            if self.cg.map.name == "索奇亞海底洞窟 地下2樓":
                self.cg.nav_to(27, 29)
            if (
                self.cg.map.name == "索奇亞海底洞窟 地下1樓"
                and self.cg.map.id == 15004
                and self.cg.map.y < 40
            ):
                self.cg.nav_to(7, 37)

            if (
                self.cg.map.name == "索奇亞"
                and self.cg.map.x < 400
                and self.cg.map.y < 296
            ):
                self.cg.nav_to(274, 294)

            if (
                self.cg.map.name == "索奇亞"
                and self.cg.map.x < 400
                and self.cg.map.y > 300
            ):
                self.cg.nav_to(356, 334)

            if self.cg.map.name == "角笛大風穴":
                self.cg.nav_to(133, 26)

            if self.cg.map.name == "索奇亞" and self.cg.map.x > 400:
                self.cg.nav_to(528, 329)

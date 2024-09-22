import random
import time
from happy.interface import Script
from happy.interface.map import MapUnit


class LiDong(Script):
    def _on_init(self):
        self.name = "里洞魔石"

    def _on_not_battle(self):

        if self.cg.map.name in ["亞諾曼城", "中央醫院"]:
            if self.cg.items.count > 10:
                self._go_to_sell()
                return
            if self.cg.player.hp_per != 100 and self.cg.player.mp_per != 100:
                self._go_to_heal()
                return

        if not self.cg.items.has_weapon:
            weapon = self.cg.items.find("弓")
            if weapon:
                self.cg.items.use(weapon)
            else:
                self._go_to_buy_weapon()
            return

        if not self.cg.items.crystal:
            crystal = self.cg.items.find("地水的水晶")
            if crystal:
                self.cg.items.use(weapon)
            else:
                self._go_to_buy_crystal()
            return

        if self.cg.items.count == 20:
            self._go_to_sell()
            return

        if (
            self.cg.player.hp_per < 30
            or self.cg.player.mp < 40
            or self.cg.pets.on_battle.hp_per < 30
        ):
            self._go_to_heal()
            return

        if self.cg.player.injury > 0 or self.cg.pets.on_battle.injury > 0:
            self._go_to_cure()
            return

        self._go_to_dungeon()

    def _nav_dungeon(self):
        pass

    def _go_to_dungeon(self):
        if self.cg.map.name == "亞諾曼城":
            if self.cg.map.location == (120, 139) or self.cg.map.location == (194, 93):
                self.cg.click("A")
                time.sleep(1)

            elif self.cg.map.x < 80:
                self.cg.nav_to(21, 126)
            else:
                self.cg.tp()
            return

        if self.cg.map.name == "德威特島":
            self.cg.nav_to(129, 295)
            return

        if self.cg.map.name == "里歐波多洞窟":

            entrance = self.cg.map.units.find(
                name=" ", type=1, flag=4096, model_id_lt=103011
            )
            if isinstance(entrance, MapUnit):
                self.cg.nav_to(entrance.location)
            else:
                self.cg.nav_to(25, 19)
            return

        if "里歐波多洞窟地下13層" in self.cg.map.name:
            self.cg.go_to(
                self.cg.map.x + random.randint(-10, 10),
                self.cg.map.y + random.randint(-10, 10),
            )
            return

        if "里歐波多洞窟地下" in self.cg.map.name:
            transports = self.cg.map.file.transports
            if len(transports) <= 1:
                self.cg.map.request_download()
                time.sleep(0.5)
            else:
                transports.sort(key=lambda x: x[2])
                x, y, _ = transports[1]
                if self.cg.map.location == (x, y):
                    self.cg.go_to(
                        self.cg.map.x + random.randint(-1, 1),
                        self.cg.map.y + random.randint(-1, 1),
                    )
                self.cg.nav_to(x, y)
            return

        self.cg.tp()

    def _go_to_sell(self):
        if self.cg.map.name != "亞諾曼城":
            self.cg.tp()
        self.cg.nav_to(132, 133)
        self.cg.dialogue_to(133, 132)

    def _go_to_hostpital(self):
        if self.cg.map.name == "亞諾曼城":
            self.cg.nav_to(116, 134)
        else:
            self.cg.tp()

    def _go_to_heal(self):
        if self.cg.map.name == "中央醫院":
            self.cg.nav_to(13, 23)
            self.cg.dialogue_to(14, 22)
        else:
            self._go_to_hostpital()

    def _go_to_cure(self):
        if self.cg.map.name == "中央醫院":
            self.cg.nav_to(9, 7)
            self.cg.dialogue_to(10, 6)
        else:
            self._go_to_hostpital()

    def _go_to_buy_crystal(self):
        if self.cg.map.name == "亞諾曼城":
            self.cg.nav_to(97, 128)
        elif self.cg.map.name == "命運小屋":
            self.cg.nav_to(15, 22)
            self.cg.dialogue_to(17, 22)
            self.cg.buy(9)
        else:
            self.cg.tp()

    def _go_to_buy_weapon(self):
        if self.cg.map.name == "亞諾曼城":
            self.cg.nav_to(100, 114)
        elif self.cg.map.name == "銳健武器店":
            self.cg.nav_to(18, 13)
            self.cg.dialogue_to(20, 13)
            self.cg.buy(3)
        else:
            self.cg.tp()


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
            if self.cg.player.endurance_points < 0:
                self.cg.player.add_point(0)
            if self.cg.player.strength_points < 125:
                self.cg.player.add_point(1)
                self.cg.player.add_point(1)
            if self.cg.player.agility_points < 60:
                self.cg.player.add_point(3)
            if self.cg.player.defense_points < 50:
                self.cg.player.add_point(2)
            if self.cg.player.level > 40 and self.cg.player.magical_points < 30:
                self.cg.player.add_point(4)
        if (
            self.cg.pets.on_battle is not None
            and self.cg.pets.on_battle.remain_points > 0
        ):
            pet = self.cg.pets.on_battle
            if pet.name in ["改造樹精"]:
                pet.add_point(0)
            if pet.name in ["小蝙蝠", "使魔", "影蝙蝠"]:
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

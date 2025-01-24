from happy import Script
from happy import MapEnum


class Zhandouxijiuzhi(Script):
    def _on_init(self):
        self.name = "战斗就职"

    @property
    def _should_sell(self):
        if self.cg.map.in_city and (self.cg.items.find("魔石") or self.cg.items.find("綠頭盔")):
            return True
        return False

    def _go_to_east_hospital(self):
        if self.cg.map.id == 1112:
            return True
        if self.cg.map.id == 1000 and self.cg.map.within(221, 83, 30):
            self.cg.nav_to(221, 83)
        else:
            self._go_to_next_transport()

    def _go_to_gonghui(self):
        if self.cg.map.enum == MapEnum.职业公会:
            return True
        if self.cg.map.enum == MapEnum.东医:
            self.cg.nav_to(18, 37)
            self.cg.dialogue_to(19, 37)
        elif self.cg.map.enum == MapEnum.西医:
            self.cg.nav_to(12, 42)
        elif self.cg.map.id == 1000 and self.cg.map.within(50, 40, 100, 130):
            self.cg.nav_to(73, 60)
        else:
            self._go_to_next_transport()

    def _go_to_24kengdao(self):
        if self.cg.map.enum == MapEnum.职业公会:
            self.cg.nav_to(9, 24)
        elif self.cg.map.id == 1000 and self.cg.map.x < 80:
            self.cg.nav_to(22, 88)
        elif self.cg.map.id == 100:
            self.cg.nav_to(351, 145)
        else:
            self._go_to_next_transport()

    def _go_to_gongjianshougonghui(self):

        if self.cg.map.name =="弓箭手公會":
            self.cg.nav_to(7, 5)
            self.cg.dialogue_to(6,4)
            self.cg.request("0 1")
        elif self.cg.map.id == 1000 and self.cg.map.within(130, 110, 200, 150):
            self.cg.nav_to(190, 133)
        else:
            self._go_to_next_transport()

    @property
    def _should_heal(self):
        return (self.cg.map.in_city or self.cg.map.in_hospital) and (
            self.cg.player.hp_per < 100 or not self.cg.pets.full_state
        )

    def _go_to_heal(self):
        if self.cg.map.id == 1112:
            self.cg.nav_to(7, 34)
            self.cg.dialogue_to(7, 33)
        else:
            self._go_to_east_hospital()

    def _on_not_moving(self):

        if self.cg.player.job_name == "見習弓箭手":
            self.cg.items.drop("平民小刀")
            self.cg.dialog.close()
            self.enable = False
            return

        tuijianxin = self.cg.items.find("推薦信")
        if tuijianxin :
            self._go_to_gongjianshougonghui()
            return
        
        if not self.cg.pets.on_battle:
            self.cg.pets.first.set_state(2)

        if self._should_sell:
            self._go_to_sell()
            return

        if self._should_heal:
            self._go_to_heal()
            return
        
        
        zhitongyao = self.cg.items.find("止痛藥")
        tongxingzheng = self.cg.items.find("試煉洞穴通行證")

        
        #买止疼药
        if not zhitongyao and not tongxingzheng:
            if self.cg.map.enum == MapEnum.东医:
                self.cg.go_to(16, 36)
                self.cg.dialogue_to(16, 35)
                if self.cg.items.gold >= 3:
                    self.cg.buy(1)
                else:
                    self.enable = False
                    print("金币不足")
            else:
                self._go_to_east_hospital()
            return
        
        #换通行证
        if zhitongyao and not tongxingzheng:
            if self.cg.map.enum == MapEnum.职业公会:
                self.cg.go_to(8, 6)
                self.cg.dialogue_to(9, 6)
                self.cg.reply()
            else:
                self._go_to_gonghui()
            return

        if tongxingzheng:
            if self.cg.map.name == "國營第24坑道 地下1樓":
                if self.cg.map.y > 15:
                    self.cg.nav_to(9, 15)
                else:
                    self.cg.nav_to(9, 5)

                if self.cg.map.location == (7, 15):
                    self.cg.go_to(7, 14)

                if self.cg.map.location == (9, 15):
                    if self.cg.team.count == 0:
                        self.cg.dialogue_to(9, 14)
                        self.cg.reply()
                    else:
                        self.cg.team.leave()
            elif self.cg.map.name == "試煉之洞窟 第1層":
                self.cg.nav_to(33, 31)
            elif self.cg.map.name == "試煉之洞窟 第2層":
                self.cg.nav_to(7, 9)
            elif self.cg.map.name == "試煉之洞窟 第3層":
                self.cg.nav_to(42, 34)
            elif self.cg.map.name == "試煉之洞窟 第4層":
                self.cg.nav_to(27, 12)
            elif self.cg.map.name == "試煉之洞窟 第5層":
                self.cg.nav_to(39, 36)
            elif self.cg.map.name == "試煉之洞窟 大廳":
                if self.cg.items.right_hand and self.cg.items.right_hand.name == "平民弓":
                    self.cg.nav_to(23, 17)
                    self.cg.dialogue_to(23, 16)
                    self.cg.reply("弓箭手")
                elif self.cg.items.use("平民弓"):
                    return
                else:
                    self.cg.nav_to(23, 23)
                    self.cg.dialogue_to(24, 24)
                    self.cg.buy(3)
            else:
                self._go_to_24kengdao()

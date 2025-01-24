from happy.interface import Script

class Yanuoman(Script):
    def _on_init(self):
        self.name = "亚诺曼城"
    
    def _on_not_battle(self):
       
        if self.cg.map.id == 1000 and self.cg.map.within(135, 120, 180, 160):
            self.cg.nav_to(162, 146)
            self.cg.click_to(163,146)
        elif self.cg.map.id == 30149:
            self.cg.go_to(16, 24)
        elif self.cg.map.id == 30010:
            self.cg.nav_to(118, 136)
            if self.cg.map.location == (118, 136) and not self.cg.dialog.is_open:
                self.cg.click("E")
                self.cg.say("S1")
            if self.cg.reply("登錄點設定為 S1 "):
                self.enable = False
                return
        else:
            self._go_to_next_transport()

        
class Falancheng(Script):
    def _on_init(self):
        self.name = "法兰定居"
    
    def _on_not_battle(self):
        if self.cg.map.id == 30010 and self.cg.map.within(148, 115, 40):
            self.cg.nav_to(148, 115)
        elif self.cg.map.id == 30149:
            self.cg.go_to(13, 8)
            self.cg.click_to(13,7)
        elif self.cg.map.id == 1000 and self.cg.map.within(162, 130, 30):
            self.cg.go_to(162, 130)
            self.cg.click_to(163,130)
        elif self.cg.map.id == 1000 and self.cg.map.within(72, 123, 5):
            self.cg.go_to(72, 123)
            self.cg.click_to(73,123)
        elif self.cg.map.id == 1164 and self.cg.map.location == (12, 6):
            self.cg.click("A")
        elif self.cg.map.id == 1000 and self.cg.map.within(230, 76, 20):
            if self.cg.go_to(230, 76):
                self.cg.click("C")
            if self.cg.reply("登錄點想設在法蘭城嗎"):
                self.enable = False
                return
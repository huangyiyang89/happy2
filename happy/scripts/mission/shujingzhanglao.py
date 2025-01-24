from happy.interface import Script

class Shujingzhanglao(Script):
    def _on_init(self):
        self.name = "树精长老"

    def _on_not_moving(self):

        shumiao = self.cg.items.find("樹苗？")
        if shumiao:
            if self.cg.map.id == 30010:
                self.cg.nav_to(163, 129)
            elif self.cg.map.name == "皇家寶石店":
                self.cg.go_to(13,11)
                self.cg.dialogue_to(13,9)
                self.cg.request("0 "+str(shumiao.index))
            else:
                self._go_to_next_transport()
            return
        
        if self.cg.map.name == "皇家寶石店":
            self.cg.go_to(0,15)
            return

        if self.cg.map.id == 30010:
            self.cg.say("/bhome")
        elif self.cg.map.name == "啟程之間":
            self.cg.nav_to(9, 23)
            self.cg.dialogue_to(8,22)
            self.cg.reply()
        elif self.cg.map.name == "法蘭城" and self.cg.map.within(130, 100, 180, 190):
            self.cg.nav_to(153, 100)
        elif self.cg.map.name == "里謝里雅堡":
            self.cg.go_to(41, 50)
        elif self.cg.map.name == "里謝里雅堡 1樓":
            self.cg.nav_to(45, 20)
        elif self.cg.map.id == 1541:
            self.cg.go_to(14, 25)
            self.cg.go_to(13, 25)
        #维诺亚传送点
        elif self.cg.map.id == 2199:
            self.cg.go_to(5,1)
        elif self.cg.map.id == 2198:
            self.cg.go_to(0,5)
        elif self.cg.map.id == 2112:
            shengmingzhihua = self.cg.items.find("生命之花")
            if shengmingzhihua:
                self.cg.go_to(15, 8)
                self.cg.dialogue_to(16, 7)
                self.cg.reply()
                if "公會會長吧" in self.cg.dialog.content:
                    self.enable = False

                    
            else:
                self.cg.go_to(9,16)
        elif self.cg.map.id == 2100:
            huoba = self.cg.items.find("火把")
            if huoba:
                self.cg.nav_to(67, 47)
            else:
                self.cg.nav_to(61, 53)
        #维诺亚医院
        elif self.cg.map.id == 2110:
            huoba = self.cg.items.find("火把")
            if not huoba:
                self.cg.nav_to(6, 5)
                self.cg.dialogue_to(7, 5)
                self.cg.reply()
            if huoba:
                self.cg.nav_to(2, 9)
        elif self.cg.map.name == "芙蕾雅":
            huoba = self.cg.items.find("火把")
            if huoba:
                if self._should_be_leader:
                    if self._expected_team_count == self.cg.team.count:
                        self.cg.nav_to(380, 353)
                    else:
                        self.cg.go_to(332, 481)
                else:
                    self.cg.go_to(331, 481)
                    self.cg.click("C")
                    self.cg.team.join()
        elif "佈滿青苔的洞窟" in self.cg.map.name:
            if self._should_go:
                self.cg.nav_dungeon()
        elif self.cg.map.name == "嘆息之森林":
            if self._should_go:
                self.cg.nav_to(29, 14)
                self.cg.click_to(29, 13)
        elif self.cg.map.name == "嘆息森林":
            self.cg.items.drop("艾里克的大劍")
            if self.cg.team.count>0:
                self.cg.team.leave()
            self.cg.go_to(27,12)
            self.cg.dialogue_to(26, 12)




        
        

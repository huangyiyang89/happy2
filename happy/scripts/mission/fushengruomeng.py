from happy.interface import Script


class Fushengruomeng(Script):
    def _on_init(self):
        self.name = "浮生若梦"

    def _on_not_moving(self):
        if self.cg.map.id == 1512:
            self.cg.reply()
        if self.cg.map.id == 65331:
            self.cg.go_to(0, 7)
        if self.cg.map.id == 65332:
            self.cg.go_to(9, 19)
        if self.cg.map.id == 65330:
            self.cg.go_to(49, 80)
        if self.cg.map.id == 65334:
            self.cg.go_to(49, 80)
        if self.cg.map.id == 65320:
            if self.cg.items.find("門的木屑"):
                self.cg.go_to(75, 19)
            else:
                self.cg.go_to(75, 38)
                self.cg.dialogue_to(75, 39)
                self.cg.reply()
        if self.cg.map.id == 65333:
            self.cg.go_to(49, 74)
            self.cg.reply()

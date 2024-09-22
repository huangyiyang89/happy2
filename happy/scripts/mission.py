from happy.interface import Script

class Szdjz(Script):
    """死者的戒指任务，新手任务"""
    def _on_init(self):
        self.name = "新手任务"

    def _on_not_moving(self):
        cg = self.cg
        if cg.is_moving or cg.battle.is_battling:
            return

        has_ring = cg.items.find("死者的戒指")
        if cg.map.id == 1530: #召唤之间
            cg.nav_to(18,6)
            cg.dialogue_to(19,6)
            #has no ring
            cg.reply("異界來的客人啊","4")
            cg.reply("什麼！你真的是嗎？","w")
            cg.reply("那麼，希望你能向我證明，你並沒有說謊。","w")
            cg.reply("我為你準備了兩條考驗之路","w")
            cg.reply("如果你想走新手之路","4")
            cg.reply("再回來找我好嗎","w")
            cg.reply("你就可以找到戒指","1")
            #has ring
            cg.reply("我之所以會召喚異界人的你來此","w")
            cg.reply("如果你真的是『開啟者』的話","w")
            cg.reply("那麼，你出去吧…","w")
            
        if cg.map.id == 1531: #回廊
            cg.nav_to(44,15) if has_ring else cg.nav_to(23,19)

        if cg.map.id == 11015: #灵堂
            cg.nav_to(31,48) if has_ring else cg.nav_to(53,2)
            cg.dialogue_to(54,2)
            cg.reply("死者的戒指是勇者的證明","4")

        if cg.map.id == 1511: #谒见之间
            cg.nav_to(7,4) if has_ring else cg.nav_to(8,19)
            cg.dialogue_to(7,3)
            cg.reply("把『死者的戒指』拿給我看吧","w")
            cg.reply("這張賞賜信給你","1")
        
        if cg.map.id == 1521: #里堡 2楼
            if cg.items.find("賞賜狀"):
                cg.nav_to(51,78)
                cg.dialogue_to(51,79)
                cg.reply("那是國王的賞賜信啊","1")
        





from happy import MapEnum
from happy.interface import Script


class Xueluanshe(Script):
    def _on_init(self):
        self.name = "去学乱射"

    def _on_not_moving(self):

        if self.cg.map.id == 30010:
            self.cg.say("/bhome")
        if self.cg.map.name == "豪華屋":
            self.cg.go_to(14, 25)
            self.cg.go_to(13, 25)

        if self.cg.map.enum == MapEnum.法兰城:
            if self.cg.map.y > 150:
                self.cg.nav_to(153, 241)  # 出南门

        # 西門-熊洞
        if self.cg.map.name == "芙蕾雅" and self._should_go:
            if self.cg.map.y > 258 and self.cg.map.y < 317:
                self.cg.nav_to(472, 316)

        # 對話進入熊洞
        if self.cg.map.location == (472, 316) and self.cg.team.is_leader:
            self.cg.team.leave()
        if self.cg.team.count == 0:
            self.cg.nav_to(473, 316)
            self.cg.dialogue_to(472, 316)
            self.cg.reply()

        # 進入熊洞后組隊
        if self.cg.map.name == "維諾亞洞穴 地下1樓":
            if (
                self._should_be_leader
                and self.cg.team.count < self._expected_team_count
            ):
                self.cg.go_to(20, 17)
            if not self._should_be_leader and self.cg.team.count == 0:
                self.cg.go_to(20, 16)
                self.cg.team.join()

        # 熊洞
        if self.cg.map.name == "維諾亞洞穴 地下1樓" and self._should_go:
            self.cg.nav_to(20, 59)
        if self.cg.map.name == "維諾亞洞穴 地下2樓" and self._should_go:
            self.cg.nav_to(24, 81)
        if self.cg.map.name == "維諾亞洞穴 地下3樓" and self._should_go:
            self.cg.nav_to(26, 64)

        # 熊洞-維諾亞村
        if self.cg.map.name == "芙蕾雅" and self._should_go:
            if 481 > self.cg.map.y > 345:
                self.cg.nav_to(330, 480)
            if self.cg.map.y > 480:
                self.cg.nav_to(343, 497)

        # 過海
        if (
            self.cg.map.name == "索奇亞海底洞窟 地下1樓"
            and self.cg.map.id == 15005
            and self._should_go
        ):
            self.cg.nav_to(18, 34)
        if self.cg.map.name == "索奇亞海底洞窟 地下2樓" and self._should_go:
            self.cg.nav_to(27, 29)
        if (
            self.cg.map.name == "索奇亞海底洞窟 地下1樓"
            and self._should_go
            and self.cg.map.id == 15004
            and self.cg.map.y < 40
        ):
            self.cg.nav_to(7, 37)
        if (
            self.cg.map.name == "索奇亞海底洞窟 地下1樓"
            and self.cg.team.count == 0
            and self.cg.map.id == 15004
            and self.cg.map.y < 40
        ):
            self.cg.nav_to(7, 37)
            if self.cg.map.location == (7, 37):
                self.cg.team.join()

        if self.cg.map.name == "索奇亞海底洞窟 地下1樓" and self.cg.map.y > 41:
            if self._should_be_leader and not self._should_go:
                self.cg.go_to(8, 43)
            if (
                not self._should_be_leader
                and self.cg.team.count == 0
                and self.cg.map.location == (8, 42)
            ):
                self.cg.team.join()
            if self._should_go:
                self.cg.go_to(11, 44)

        if (
            self.cg.map.name == "索奇亞"
            and self.cg.map.x < 400
            and self.cg.map.y < 296
            and self._should_go
        ):
            self.cg.nav_to(274, 294)

        if self.cg.map.name == "索奇亞" and self.cg.map.x < 400 and self.cg.map.y > 300:
            self.cg.nav_to(356, 334)

        if self.cg.map.name == "角笛大風穴":
            self.cg.nav_to(133, 26)

        if self.cg.map.name == "索奇亞" and self.cg.map.x > 400:
            self.cg.nav_to(528, 329)

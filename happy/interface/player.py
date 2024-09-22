from happy.interface.mem import InterfaceBase

class Player(InterfaceBase):

    @property
    def hp(self):
        hp_str = self.mem.read_string(0x00CB27EC, 4)
        return int(hp_str)

    @property
    def hp_max(self):
        hp_max_str = self.mem.read_string(0x00CB27F1, 4)
        return int(hp_max_str)

    @property
    def hp_lost(self):
        return self.hp_max - self.hp

    @property
    def hp_per(self):
        if self.hp_max:
            return int(self.hp / self.hp_max * 100)
        return 0

    @property
    def mp_per(self):
        if self.mp_max:
            return int(self.mp / self.mp_max * 100)
        return 0

    @property
    def mp(self):
        mp_str = self.mem.read_string(0x00CB7900, 4)
        return int(mp_str)

    @property
    def mp_lost(self):
        return self.mp_max - self.mp

    @property
    def mp_max(self):
        mp_max_str = self.mem.read_string(0x00CB7905, 4)
        return int(mp_max_str)

    @property
    def level(self):
        return self.mem.read_int(0x00F4C2F4)

    @property
    def value_recovery(self):
        """回复
        Returns:
            _type_: _description_
        """
        return self.mem.read_int(0x00F4C398)

    @property
    def injury(self):
        """受伤程度 25/50/75/100"""
        return self.mem.read_int(0x00F4C3E4)

    @property
    def job_name(self):
        return self.mem.read_string(0x00E8D6D0)

    @property
    def name(self):
        """encoding="big5hkscs"""
        return self.mem.read_string(0x00F4C3F8, encoding="big5hkscs")

    @property
    def remain_points(self):
        """剩余点数"""
        return self.mem.read_int(0x00CB0AF4)

    @property
    def endurance_points(self):
        return self.mem.read_int(0x00F4C368)

    @property
    def strength_points(self):
        return self.mem.read_int(0x00F4C36C)

    @property
    def defense_points(self):
        return self.mem.read_int(0x00F4C370)

    @property
    def agility_points(self):
        return self.mem.read_int(0x00F4C374)

    @property
    def magical_points(self):
        return self.mem.read_int(0x00F4C378)

    def add_point(self, index:int):
        """加点 0 体力 1 力量 2 防御 3 敏捷 4 魔法
        """
        if self.remain_points > 0:
            self.mem.decode_send(f"IHw {index}")
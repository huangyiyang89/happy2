from happy.interface.mem import CgMem, InterfaceBase


class Pet(InterfaceBase):
    def __init__(self, mem: CgMem, index: int) -> None:
        super().__init__(mem)
        self.index = index

    def add_point(self, index):
        self.mem.decode_send(f"kjSK {self.index} {index}")

    @property
    def name(self):
        return self.mem.read_string(0x00ED5694 + self.index * 0x5110)

    @property
    def state(self):
        return self.mem.read_short(0x00ED5692 + self.index * 0x5110)

    @property
    def hp(self):
        return self.mem.read_xor_value(0x00ED4FF8 + self.index * 0x5110)

    @property
    def hp_max(self):
        return self.mem.read_xor_value(0x00ED5008 + self.index * 0x5110)

    @property
    def hp_per(self):
        if self.hp_max:
            return int(self.hp / self.hp_max * 100)
        return 0

    @property
    def mp(self):
        return self.mem.read_xor_value(0x00ED5018 + self.index * 0x5110)

    @property
    def mp_max(self):
        return self.mem.read_xor_value(0x00ED5028 + self.index * 0x5110)

    @property
    def mp_per(self):
        if self.mp_max:
            return int(self.mp / self.mp_max * 100)
        return 0

    @property
    def remain_points(self):
        return self.mem.read_int(0x00ED5054 + self.index * 0x5110)

    @property
    def injury(self):
        return self.mem.read_int(0x00ED50BC + self.index * 0x5110)

    def add_point(self, index):
        #index 0 体力 1力量 2防御 3敏捷 4魔法
        self.mem.decode_send(f"kjSK {self.index} {index}")

    def set_state(self, state):
        """0 休息 1 待命 2 战斗"""
        state_list = ["0"] * 5
        state_list[self.index] = str(state)
        state_str = " ".join(state_list)
        self.mem.decode_send(f"LKQy {state_str}")

class PetCollection(InterfaceBase):
    def __init__(self, mem: CgMem) -> None:
        super().__init__(mem)

    def __iter__(self):
        for i in range(5):
            pet = Pet(self.mem, i)
            if pet.name:
                yield pet

    @property
    def on_battle(self):
        for pet in self:
            if pet.state == 2:
                return pet
        return None

    def __getitem__(self, index):
        for pet in self:
            if pet.index == index:
                return pet
        return None

    @property
    def full_state(self):
        for pet in self:
            if pet.hp_per < 100 or pet.mp_per < 100:
                return False
        return True

    @property
    def full_health(self):
        for pet in self:
            if pet.injury > 0:
                return False
        return True

    @property
    def first(self):
        return next(iter(self), None)
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

class PetCollection(InterfaceBase):
    def __init__(self, mem: CgMem) -> None:
        super().__init__(mem)
        self._pets: list[Pet] = []
        for i in range(5):
            pet = Pet(mem, i)
            if pet.name:
                self._pets.append(pet)

    @property
    def on_battle(self):
        for pet in self._pets:
            if pet.state == 2:
                return pet
        return None

    def __getitem__(self, index):
        for pet in self._pets:
            if pet.index == index:
                return pet
        return None

    @property
    def full_state(self):
        for pet in self._pets:
            if pet.hp_per < 100 or pet.mp_per < 100:
                return False
        return True

    @property
    def full_health(self):
        for pet in self._pets:
            if pet.injury > 0:
                return False
        return True

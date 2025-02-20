from happy.interface.mem import LocationBase

class Team(LocationBase):
    # short valid;
    # short padding;
    # int unit_id;
    # int maxhp;
    # int mp;
    # int hp;
    # int unk;
    # char name[20];
    # void *actor;
    @property
    def count(self):
        party1 = self.mem.read_short(0x00FFD000)
        party2 = self.mem.read_short(0x00FFD030)
        party3 = self.mem.read_short(0x00FFD060)
        party4 = self.mem.read_short(0x00FFD090)
        party5 = self.mem.read_short(0x00FFD0C0)
        return party1 + party2 + party3 + party4 + party5

    @property
    def is_leader(self):
        leader = self.mem.read_short(0x00F4C47C)
        return leader == 1
    
    def join(self):
        self.mem.decode_send(f"zn {self._x_62} {self._y_62} 1")

    def leave(self):
        self.mem.decode_send(f"zn {self._x_62} {self._y_62} 0")
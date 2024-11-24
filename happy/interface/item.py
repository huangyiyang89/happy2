from happy.interface.mem import CgMem, InterfaceBase, LocationBase
from happy.util import b62

_foods = [
    ("蕃茄醬", 30),
    ("麵包", 100),
    ("白飯", 30),
    ("美乃滋芝麻拌飯", 300),
    ("蛋飯", 50),
    ("蛋包飯", 150),
    ("法國麵包", 200),
    ("炒麵", 250),
    ("青椒肉絲", 300),
    ("燒雞", 350),
    ("親子丼", 400),
    ("漢堡", 450),
    ("星鰻飯糰", 500),
    ("醬油豬骨拉麵", 400),
    ("炒麵麵包", 550),
    ("壽喜鍋", 600),
    ("咖哩飯", 650),
    ("韓式泡菜飯", 700),
    ("螃蟹鍋", 750),
    ("牛排", 800),
    ("醋飯壽司", 850),
    ("豪華壽司組", 900),
    ("魚翅湯", 100),
    ("鱉料理", 1200),
    ("韓式海鮮鍋", 1400),
    ("紙包雞", 600),
    ("叉燒飯", 1400),
]


_drugs = [
    ("特效OK繃", 200),
    ("生命力回復藥 （100）", 100),
    ("生命力回復藥 （150)", 150),
    ("生命力回復藥 （200）", 200),
    ("生命力回復藥 （250）", 250),
    ("生命力回復藥 （300）", 300),
    ("生命力回復藥 （400）", 400),
    ("生命力回復藥 （500）", 500),
    ("生命力回復藥 （600）", 600),
    ("生命力回復藥 （800）", 800),
    ("生命力回復藥 （1000）", 1000),
    ("生命力回復藥 （1400）", 1400),
]


class Item:
    def __init__(self, index: int, name: str, count: int):
        self._index = index
        self._name = name
        self._count = count

    @property
    def index(self):
        return self._index

    @property
    def index_62(self):
        return b62(self.index)

    @property
    def name(self):
        return self._name

    @property
    def count(self):
        return self._count

    @property
    def food_restore(self):
        for food in _foods:
            if self._name == food[0]:
                return food[1]
        return 0

    @property
    def is_food_box(self):
        if "』盒" in self.name:
            for food in _foods:
                if food[0] in self._name:
                    return True
        return False

    @property
    def is_drug_box(self):
        if "』盒" in self.name:
            for drug in _drugs:
                if drug[0] in self._name:
                    return True
        return False

    @property
    def drug_restore(self):
        for drug in _drugs:
            if self._name == drug[0]:
                return drug[1]
        return 0


class ItemCollection(LocationBase):

    def __iter__(self):
        for i in range(28):
            valid = self.mem.read_short(0x00F4C494 + 0xC5C * i)
            if valid:
                name = self.mem.read_string(0x00F4C494 + 2 + 0xC5C * i, 46)
                count = self.mem.read_int(0x00F4C494 + 3140 + 0xC5C * i)
                item = Item(i, name, count)
                yield item

    def use(self, item: str | Item, target: str | int = 0):

        if isinstance(item, str):
            item_to_use = self.find(item)
        if isinstance(item, Item):
            item_to_use = item
        if item_to_use:
            self.mem.decode_send(
                f"Ak {self._x_62} {self._y_62} {item_to_use.index_62} {target}"
            )

    def drop(self, *args):
        for item in args:
            if isinstance(item, Item):
                self.mem.decode_send(
                    f"QpfE {self._x_62} {self._y_62} 0 {item.index_62}"
                )
            if isinstance(item, str):
                item_to_find = self.find(item)
                if item_to_find:
                    self.mem.decode_send(
                        f"QpfE {self._x_62} {self._y_62} 0 {item_to_find.index_62}"
                    )
                    return



    @property
    def gold(self):
        return self.mem.read_int(0x00F4C3EC)

    @property
    def first_food(self):
        return next((item for item in self if item.food_restore > 0), None)

    @property
    def first_drug(self):
        return next((item for item in self if item.drug_restore > 0), None)

    @property
    def first_food_box(self):
        return next((item for item in self if item.is_food_box), None)

    @property
    def first_drug_box(self):
        return next((item for item in self if item.is_drug_box), None)

    @property
    def bags(self):
        return (item for item in self if item.index >= 8)

    @property
    def gears(self):
        return (item for item in self if item.index < 8)

    def find(self, item_name: str = "", quantity=0):
        """模糊匹配包含item_name的第一个物品"""
        for item in self:
            if item_name in item.name and item.count >= quantity:
                return item
        return None

    def get(self, index):
        for item in self:
            if item.index == index:
                return item
        return None

    @property
    def count(self):
        """背包内物品数量，不包括装备"""
        counter = 0
        for i in range(8, 28):
            valid = self.mem.read_short(0x00F4C494 + 0xC5C * i)
            if valid:
                counter += 1
        return counter

    @property
    def left_hand(self):
        return self.get(3)

    @property
    def right_hand(self):
        return self.get(2)

    @property
    def has_weapon(self):
        return self.left_hand or self.right_hand

    @property
    def crystal(self):
        return self.get(7)

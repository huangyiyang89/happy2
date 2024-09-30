import random
import time
import math
import logging
from happy.interface.mem import CgMem, InterfaceBase


def _bits_count(n):
    """计算二进制数中有多少个1

    Args:
        n (_type_): _description_

    Returns:
        _type_: _description_
    """
    count = 0
    while n:
        count += n & 1
        n >>= 1
    return count


class Unit:
    def __init__(self, data_list: list) -> None:
        if len(data_list) != 12:
            raise Exception("Unit init error")
        self._data_list = data_list

    @property
    def position(self):
        return int(self.position_hex, 16)

    @property
    def position_hex(self):
        return self._data_list[0]

    @property
    def name(self):
        return self._data_list[1]

    @property
    def level(self):
        return int(self._data_list[4], 16)

    @property
    def hp(self):
        return int(self._data_list[5], 16)

    @property
    def hp_max(self):
        return int(self._data_list[6], 16)

    @property
    def hp_per(self):
        return self.hp / self.hp_max * 100

    @property
    def hp_lost(self):
        return self.hp_max - self.hp

    @property
    def mp(self):
        return int(self._data_list[7], 16)

    @property
    def mp_max(self):
        return int(self._data_list[8], 16)

    @property
    def mp_per(self):
        return self.mp / self.mp_max * 100

    @property
    def mp_lost(self):
        return self.mp_max - self.mp

    @property
    def is_enemy(self):
        return self.position > 9

    @property
    def is_uncontrolled(self):
        try:
            flag = self._data_list[9][5]
            if flag == "2" or flag == "4":
                return True
        except (IndexError, TypeError):
            logging.warning(f"is_uncontrolled IndexError _data_list = {self._data_list}")
        return False

    @property
    def unknown3(self):
        return self._data_list[3]

    @property
    def unknown9(self):
        return self._data_list[9]

    @property
    def unknown10(self):
        return self._data_list[10]

    @property
    def unknown11(self):
        return self._data_list[11]


class UnitCollection(InterfaceBase):
    def __init__(self, mem: CgMem) -> None:
        super().__init__(mem)
        self._buffer_cache = ""
        self._units: list[Unit] = []

    @property
    def _buffer(self):
        index = self.mem.read_int(0x00590754)
        return self.mem.read_string(
            0x00591774 + index * 0x1000, 1000, encoding="big5hkscs"
        )

    def _update(self):
        if self._buffer == self._buffer_cache:
            return
        self._units.clear()
        data_array = self._buffer.split("|")
        for i in range(0, len(data_array) - 12, 12):
            _unit = Unit(data_array[i : i + 12])
            self._units.append(_unit)

    @property
    def _update_units(self):
        self._update()
        return self._units

    @property
    def _player_position(self):
        return self.mem.read_int(0x005989DC)

    @property
    def _pet_position(self):
        return (
            self._player_position + 5
            if self._player_position < 5
            else self._player_position - 5
        )

    @property
    def player(self):
        return self.get(self._player_position)

    @property
    def pet(self):
        return self.get(self._pet_position)

    def get(self, position):
        return next(
            (unit for unit in self._update_units if unit.position == position), None
        )

    @property
    def random_choice_enemy(self):
        excepts = []
        for unit in self._update_units:
            if unit.position > 14:
                excepts.append(unit.position - 5)
        fronts = [unit for unit in self.enemies if unit.position not in excepts]
        return random.choice(fronts)

    @property
    def friends(self):
        return [unit for unit in self._update_units if unit.position < 10]

    @property
    def enemies(self):
        return [unit for unit in self._update_units if unit.position >= 10]

    def get_lowest_hp_per_target(self):
        if len(self.friends) == 0:
            return None
        return min(self.friends, key=lambda unit: unit.hp_per)

    def _get_cross_target(self, units: list[Unit]):
        # 强力位二进制表示
        crosses = [
            0b11100100000000000000,
            0b11010010000000000000,
            0b10101001000000000000,
            0b01010000100000000000,
            0b00101000010000000000,
            0b10000111000000000000,
            0b01000110100000000000,
            0b00100101010000000000,
            0b00010010100000000000,
            0b00001001010000000000,
            0b00000000001110010000,
            0b00000000001101001000,
            0b00000000001010100100,
            0b00000000000101000010,
            0b00000000000010100001,
            0b00000000001000011100,
            0b00000000000100011010,
            0b00000000000010010101,
            0b00000000000001001010,
            0b00000000000000100101,
        ]

        # 场上存在符合条件的友方单位二进制表示是否存在
        units_bit = 0
        for unit in units:
            units_bit += 1 << (19 - unit.position)
        ret_unit = None
        for unit in units:
            count = _bits_count(units_bit & crosses[unit.position])
            if count == 4:
                return unit
            if count == 3:
                ret_unit = unit
        return ret_unit

    def get_line_target(self) -> Unit:
        fronts = [enemy for enemy in self.enemies if enemy.position > 14]
        backs = [enemy for enemy in self.enemies if enemy.position <= 14]
        front_count = sum(fronts) if fronts else 0
        back_count = sum(backs) if backs else 0
        targets = fronts if front_count >= back_count else backs
        return next(targets)

    def get_cross_enemy_target(self):
        return self._get_cross_target(self.enemies)

    def get_cross_friend_target(self, hp_per_lower_than=70):

        return self._get_cross_target(
            unit for unit in self.friends if unit.hp_per <= hp_per_lower_than
        )

    def get_random_target(self):
        return random.choice(self.enemies)


class Skill:
    def __init__(self, index: int, name: str, level: int, min_cost: int, position: int):
        self._index = index
        self._name = name
        self._level = level
        self._min_cost = min_cost
        self._position = position

    @property
    def index(self):
        return self._index

    @property
    def name(self):
        return self._name

    @property
    def level(self):
        return self._level

    @property
    def min_cost(self):
        return self._min_cost

    @property
    def position(self):
        return self._position

    def get_efficient_level(self, enemies_count):
        if enemies_count > 5:
            return self.level
        if self.name == "亂射":
            return enemies_count * 2 - 1
        if self.name == "氣功彈":
            if enemies_count > 4:
                return self.level
            if enemies_count == 4:
                return 7
            if enemies_count == 3:
                return 4
            if enemies_count == 2:
                return 2
        return self.level


class SkillCollection(InterfaceBase):
    def __init__(self, mem: CgMem) -> None:
        super().__init__(mem)
        self._skills: list[Skill] = []

    def _update(self):
        self._skills.clear()
        for i in range(0, 13):
            offset = i * 0x4C4C
            name = self.mem.read_string(0x00E8D6EC + offset)
            if len(name) > 0:
                level = self.mem.read_int(0x00E8D708 + offset)
                position = self.mem.read_int(0x00E8D724 + offset)
                min_cost = self.mem.read_int(0x00E8D7A4 + offset + 0x94 * (1 - 1))
                skill = Skill(i, name, level, min_cost, position)
                self._skills.append(skill)

    def get(self, name):
        self._update()
        return next((skill for skill in self._skills if skill.name == name), None)

    @property
    def default(self):
        aoe_skills = [
            "亂射",
            "氣功彈",
            "刀刃亂舞",
            "因果報應",
            "追月",
            "月影",
            "精神衝擊波",
            "超強隕石魔法",
            "超強冰凍魔法",
            "超強火焰魔法",
            "超強風刃魔法",
        ]
        self._update()
        valid_flag = self.mem.read_int(0x0059893C)
        for skill in self._skills:
            valid = valid_flag & 1 << skill.index == 1
            if valid and skill.name in aoe_skills:
                return skill
        return None


class BattlePlayer(InterfaceBase, Unit):
    def __init__(self, mem: CgMem, unit: Unit) -> None:
        InterfaceBase.__init__(self, mem)
        Unit.__init__(self, unit._data_list)
        self.skills = SkillCollection(self.mem)

    def _execute_player_command(self, command: str):
        player_buffer_addr = 0x00543F84
        player_flag_addr = 0x0048F9F7
        self.mem.write_string(player_buffer_addr, command + "\0")
        self.mem.write_bytes(player_flag_addr, bytes.fromhex("90 90"), 2)
        time.sleep(0.1)
        self.mem.write_string(player_buffer_addr, "G\0")
        self.mem.write_bytes(player_flag_addr, bytes.fromhex("74 5E"), 2)

    def cast(self, skill: Skill, unit: Unit = None, use_level=11):
        player_level = self.mem.read_int(0x00F4C2F4)
        max_ability_level = math.floor(player_level / 10) + 1

        player_mp = int(self.mem.read_string(0x00CB7900, 4))
        max_mp_level = 11
        for i in range(skill.level, 0, -1):
            cost = self.mem.read_int(0x00E8D7A4 + skill.index * 0x4C4C + 0x94 * (i - 1))
            if player_mp >= cost:
                max_mp_level = i
                break

        can_cast_level = min(skill.level, use_level, max_ability_level, max_mp_level)
        position = unit.position if unit is not None else 0
        if "強力" in skill.name:
            position = position + 0x14
        if "超強" in skill.name:
            position = 0x29 if unit.is_enemy else 0x28

        self._execute_player_command(
            f"S|{skill.index:X}|{can_cast_level-1:X}|{position:X}"
        )

    def cast_default(self, units: UnitCollection):
        """使用清怪技能，无技能或mp不足使用普通攻击"""
        skill = self.skills.default

        if skill and self.mp >= skill.min_cost:

            if skill.name == "因果報應" or skill.name == "精神衝擊波":
                self.cast(skill, units.get_line_target())
                return

            self.cast(
                skill,
                units.random_choice_enemy,
                skill.get_efficient_level(len(units.enemies)),
            )
            return

        self.attack(units.random_choice_enemy)

    def use_item(self, item, unit: Unit | None = None):
        """使用物品，默认对玩家使用"""
        index = getattr(item, "index", item)
        order = "I|" + hex(index)
        if unit is not None:
            order += "|" + unit.position_hex
        else:
            order += "|" + self.position_hex

        self._execute_player_command(order)

    def attack(self, units: Unit | list[Unit] | None = None):
        position_hex = units.position_hex if units else self.position_hex
        self._execute_player_command(f"H|{position_hex}")

    def guard(self):
        self._execute_player_command("G\0")


class PetSkill:

    def __init__(self, index, name, cost) -> None:
        self._index = index
        self._name = name
        self._cost = cost

    @property
    def index(self):
        return self._index

    @property
    def name(self):
        return self._name

    @property
    def cost(self):
        return self._cost


class BattlePet(InterfaceBase, Unit):
    def __init__(self, mem: CgMem, unit: Unit) -> None:
        InterfaceBase.__init__(self, mem)
        Unit.__init__(self, unit._data_list)

    @property
    def index(self):
        for i in range(5):
            if self.mem.read_short(0x00ED5692 + i * 0x5110) == 2:
                return i

    @property
    def skills(self):
        index = self.index
        for i in range(10):
            name = self.mem.read_string(0x00ED50C6 + index * 0x5110 + i * 0x8C)
            cost = self.mem.read_int(0x00ED5144 + index * 0x5110 + i * 0x8C)
            if len(name) > 0:
                skill = PetSkill(i, name, cost)
                yield skill

    def get_skill(self, *skill_names):
        """获得第一个名字包含 *skill_names 的PetSkill"""
        for skill in self.skills:
            for skill_name in skill_names:
                if skill_name in skill.name:
                    return skill
        return None

    def _execute_pet_command(self, command="W|0|E"):
        guard = self.get_skill("防禦", "明鏡止水", "座騎")
        flag = 1 << guard.index
        self.mem.write_short(0x005988B0, flag)
        # hook
        self.mem.write_string(0x00543EC0, command.ljust(8, "\0"))
        self.mem.write_bytes(0x00475A8C, bytes.fromhex("90 90"), 2)
        self.mem.write_bytes(0x00CDA984, bytes.fromhex("02"), 1)
        # 骑乘
        self.mem.write_bytes(0x00475D92, bytes.fromhex("90 90"), 2)
        time.sleep(0.1)
        # 还原
        self.mem.write_string(0x00543EC0, r"W|%X|%X" + "\0")
        self.mem.write_bytes(0x00475A8C, bytes.fromhex("74 73"), 2)
        # 骑乘
        self.mem.write_bytes(0x00475D92, bytes.fromhex("74 6E"), 2)

    def cast(self, skill: PetSkill | None = None, unit: Unit | None = None):
        position = unit.position if unit else self.position
        if skill and self.mp >= skill.cost:
            if "強力" in skill.name:
                position = position + 0x14
            if "超強" in skill.name:
                position = 0x29 if unit.is_enemy else 0x28
            self._execute_pet_command(f"W|{skill.index:X}|{position:X}")
        else:
            self.attack(unit)

    def attack(self, unit: Unit | None = None):
        skill = self.get_skill("攻擊")
        position_hex = unit.position_hex if unit else self.position_hex
        self._execute_pet_command(f"W|{skill.index:X}|{position_hex}")

    def cast_default(self, units: UnitCollection):
        if self.hp_per < 70:
            heal_skill = self.get_skill("吸血", "明鏡止水")
            if heal_skill and self.mp >= heal_skill.cost:
                self.cast(heal_skill, units.random_choice_enemy)
                return

        power_magic = self.get_skill(
            "強力隕石魔法", "強力冰凍魔法", "強力火焰魔法", "強力風刃魔法"
        )
        cross_target = units.get_cross_enemy_target()
        if power_magic and cross_target:
            self.cast(power_magic, cross_target)
            return

        self.cast(next(self.skills), units.random_choice_enemy)


class Battle(InterfaceBase):

    def __init__(self, mem: CgMem) -> None:
        super().__init__(mem)
        self._units = UnitCollection(mem)

    @property
    def player(self):
        unit_player = self._units.player
        if unit_player:
            return BattlePlayer(self.mem, unit_player)
        return None

    @property
    def pet(self):
        if self._units.pet:
            return BattlePet(self.mem, self._units.pet)
        return None

    @property
    def units(self):
        return self._units

    @property
    def is_waiting_anime(self) -> bool:
        """等待服务器返回

        Returns:
            bool: _description_
        """
        a = self.mem.read_int(0x005988AC)
        b = self.mem.read_int(0x00598940)
        return a != b

    @property
    def is_battling(self) -> bool:
        """state == 10"""
        return self.mem.read_int(0x00F62930) == 10

    @property
    def is_player_turn(self) -> bool:
        """人物行动时为1 宠物行动时为4 行动结束为5 登出以后再进游戏都为1"""
        return (
            self.mem.read_int(0x00598974) == 1 and self.mem.read_short(0x0072B9D0) == 3
        )

    @property
    def is_pet_turn(self) -> bool:
        """人物行动时为1 宠物行动时为4 行动结束为5 登出以后再进游戏都为1"""
        return (
            self.mem.read_int(0x00598974) == 4 and self.mem.read_short(0x0072B9D0) == 3
        )

    @property
    def is_player_second_turn(self) -> bool:
        return self.is_player_turn and self.mem.read_int(0x0059892C) == 1

    @property
    def round(self) -> int:
        a = self.mem.read_int(0x005988AC)
        b = self.mem.read_int(0x00598940)
        return min(a, b)

import os
import struct
import pickle
import time
import csv
import logging
import hashlib
from enum import Enum
from happy.interface.mem import CgMem, InterfaceBase
from happy.util.path_search import merge_path, a_star_search
from happy.util import b62, log_execution_time
from typing import Literal

# region __map_object_dict
_object_dict_pkl_path = "./data/map/object_dict.pkl"


def _dump_object_dict(cg_path="C:/BlueCrossgate/"):
    # 读取并解析地图信息
    def read_and_parse_file(file_path):
        map_object_dict = {}
        record_format = "lLLllllBBB5sl"
        with open(file_path, "rb") as file:
            while True:
                data = file.read(40)
                if not data:
                    break
                record = struct.unpack(record_format, data)
                id = record[11]
                east = record[7]
                south = record[8]
                flag = record[9]

                if id > 0 and flag == 0:
                    if (
                        id in map_object_dict
                        and east * south
                        < map_object_dict[id][0] * map_object_dict[id][1]
                    ):
                        print("发现更大范围", id, map_object_dict[id])
                        continue
                    map_object_dict[id] = [east, south]
        return map_object_dict

    graphic_info_files = [
        "bin/GraphicInfo_66.bin",
        "bin/GraphicInfoEX_5.bin",
        "bin/GraphicInfoV3_19.bin",
        "bin/GraphicInfo_Joy_54.bin",
        "bin/GraphicInfo_Joy_CH1.bin",
        "bin/GraphicInfo_Joy_EX_9.bin",
        "bin/Puk3/Graphicinfo_PUK3_1.bin",
        "bin/Puk2/GraphicInfo_PUK2_2.bin",
    ]

    map_object_dict = {}
    for file in graphic_info_files:
        data = read_and_parse_file(cg_path + file)
        map_object_dict.update(data)

    with open(_object_dict_pkl_path, "wb") as f:
        pickle.dump(map_object_dict, f)

    return map_object_dict


def _load_object_dict() -> dict:
    if os.path.exists(_object_dict_pkl_path):
        with open(_object_dict_pkl_path, "rb") as f:
            map_object_dict = pickle.load(f)
        return map_object_dict
    else:
        map_object_dict = _dump_object_dict()
        return map_object_dict


_object_dict = _load_object_dict()
# endregion


class MapFile:
    def __init__(self, path: str) -> None:

        self.path: str = path
        self.width_east: int = 0
        self.height_south: int = 0
        self._flag_data: list[list] = []
        self._transports = []
        self._last_hash = ""
        self._is_full_downloaded = False
        self._last_read_time = 0

    def hash(self):
        """读取整个文件md5值"""
        md5 = hashlib.md5()
        try:
            with open(self.path, "rb") as file:
                data = file.read()
                md5.update(data)
            return md5.hexdigest()
        except FileNotFoundError:
            logging.critical(f"hash() 文件 {self.path} 不存在。")

    @property
    def read_after(self):
        """上次成功读取后到现在的秒数"""
        return time.time() - self._last_read_time

    @property
    def transports(self):
        """
        读取之前使用read() 方法 \n
        包含出入口水晶和上下楼梯
        如果地图未完全读取，可能还需要请求地图数据
        """
        return self._transports

    @property
    def is_full_downloaded(self):
        return self._is_full_downloaded

    @property
    def is_dungeon(self):
        return "map\\0\\" not in self.path

    @property
    def _pickle_path(self):
        """example data\\map\\0\\1530.dat"""
        return "data\\map\\" + self.path.split("map\\")[1]

    def dump_flag_data_to_csv(self):
        with open(self._pickle_path + ".csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            for row in self._flag_data:
                writer.writerow(row)

    def pickle_dump_flag_data(self):
        if not self._flag_data:
            return

        directory = os.path.dirname(self._pickle_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(self._pickle_path, "wb") as f:
            pickle.dump(self._flag_data, f)
            logging.debug(f"Dump map flag data to {self._pickle_path}")

    def pickle_load_flag_data(self):
        try:
            with open(self._pickle_path, "rb") as f:
                self._flag_data = pickle.load(f)
        except FileNotFoundError:
            print(f"load_flag_data 文件 {self._pickle_path} 不存在。")
        except pickle.UnpicklingError as e:
            print(f"反序列化文件 {self._pickle_path} 时出现错误：{e}")
        except Exception as e:
            print(f"发生未知错误：{e}")

    def read(self):
        """
        读取整个文件对比md5，如果与上次读取一致则忽略 \n
        """

        hash = self.hash()
        if self._last_hash == hash:
            logging.debug(f"{self.path} READ MD5一致 使用缓存")
            return True

        logging.debug(f"READ {self.path}")

        full_downloaded_temp = True
        try:
            with open(self.path, "rb") as file:
                header = file.read(20)
                magic_word, self.width_east, self.height_south = struct.unpack(
                    "3s9x2I", header
                )
                if magic_word != b"MAP":
                    raise Exception("read error not cg map file")
                data_length = self.width_east * self.height_south * 2
                ground_bytes = file.read(data_length)
                object_bytes = file.read(data_length)
                flag_bytes = file.read(data_length)

                self._flag_data = [
                    [0 for _ in range(self.width_east)]
                    for _ in range(self.height_south)
                ]
                self._transports = []
                for i in range(0, self.height_south):
                    for j in range(0, self.width_east):
                        pointer = j + i * self.width_east
                        ground = struct.unpack(
                            "H",
                            ground_bytes[(pointer) * 2 : (pointer) * 2 + 2],
                        )[0]
                        object_id = struct.unpack(
                            "H",
                            object_bytes[(pointer) * 2 : (pointer) * 2 + 2],
                        )[0]
                        flag = struct.unpack(
                            "H",
                            flag_bytes[(pointer) * 2 : (pointer) * 2 + 2],
                        )[0]

                        if ground in _object_dict or ground == 100:
                            self._flag_data[i][j] = 1

                        if flag == 0:
                            full_downloaded_temp = False

                        # flag == 49162是出口切换地图 49155是水晶传送和上下楼梯 49152正常通过 49154遭遇战斗 49163房屋 0为未探索
                        if flag == 49155:
                            self._transports.append((j, i, object_id))

                        if (
                            flag != 49162
                            and flag != 49155
                            and flag != 49152
                            and flag != 49154
                            and flag != 49163
                            and flag != 0
                        ):

                            logging.error(f"flag error {flag}, {j}, {i}")

                        # 地上不可通过物件
                        if object_id in _object_dict:
                            e, s = _object_dict[object_id]
                            for l in range(s):
                                for m in range(e):
                                    self._flag_data[i - l][j + m] = 1

            self._is_full_downloaded = full_downloaded_temp
            self._last_hash = hash
            self._last_read_time = time.time()

            logging.debug(f"地图 {self.path} 读取成功。")
        except FileNotFoundError:
            logging.critical(f"文件 {self.path} 不存在。")
        except Exception as e:
            logging.error(f"文件 {e} 读取失败。")

    @property
    def flag_data(self):
        """
        读取之前使用read() 方法 \n
        self.flag_data[南][东] 0表示可通过 1表示有障碍"""
        return self._flag_data

    def check_flag(self, x: int | tuple, y: int = None):
        if y is None:
            if isinstance(x, tuple) and len(x) == 2:
                x, y = x
            else:
                raise ValueError("Expected a tuple with two elements for coordinates.")
        try:
            return self.flag_data[y][x] == 0
        except IndexError:
            return False


class MapUnit:
    def __init__(
        self,
        valid: int,
        type: int,
        id: int,
        model_id: int,
        location: tuple,
        level: int,
        count: int,
        name: str,
        nick_name: str,
        title: str,
        item_name: str,
        flag: int,
        injury: int,
    ):
        self.valid = valid
        self.type = type
        self.id = id
        self.model_id = model_id
        self.location = location
        self.level = level
        self.count = count
        self.name = name
        self.nick_name = nick_name
        self.title = title
        self.item_name = item_name
        self.flag = flag
        self.injury = injury

    def __str__(self):
        return (
            f"MapUnit(valid={self.valid}, type={self.type}, id={self.id}, model_id={self.model_id}, "
            f"location={self.location}, level={self.level}, count={self.count}, "
            f"name='{self.name}', nick_name='{self.nick_name}', title='{self.title}', "
            f"item_name='{self.item_name}', flag={self.flag}, injury={self.injury})"
        )


class MapUnitCollection(InterfaceBase):

    # 玩家 type == 8 and flag = 256
    # 物品 type == 2 and flag = 1024
    # 留言板 type == 17 flag == 4096
    # NPC type == 1 flag == 4096
    # 宠物 type == 1 flag == 512
    # 金币 type ==4 flag ==2048
    # injury 4096 店铺

    def find_npc(self, *names):
        for name in names:
            unit = self.find(name=name, type=1, flag=4096)
            if unit:
                return unit
        return None

    def find_location(self, x: int | tuple, y: int = None):
        if y is None:
            target = x
        else:
            target = (x, y)
        for unit in self:
            if unit.location == target:
                return unit
        return None

    def find_item(self, *names):
        for name in names:
            unit = self.find(name=name, type=2, flag=1024)
            if unit:
                return unit
        return None

    def find_items(self, *names):
        items = []
        for name in names:
            unit = self.find(name=name, type=2, flag=1024)
            if unit:
                items.append(unit)
        return items

    def find(self, name, type, flag, model_id_lt=0, injury=0):
        for unit in self:
            if (
                unit.name == name
                and unit.type == type
                and unit.flag == flag
                and unit.model_id > model_id_lt
                and unit.injury == injury
            ):
                return unit
        return None

    def __iter__(self):
        for i in range(400):
            valid = self.mem.read_short(0x005991F8 + i * 0x13C)
            if valid == 0:
                continue
            type = self.mem.read_short(0x005991F8 + 2 + i * 0x13C)
            id = self.mem.read_int(0x005991F8 + 4 + i * 0x13C)
            model_id = self.mem.read_int(0x005991F8 + 8 + i * 0x13C)
            x = self.mem.read_xor_value(0x005991F8 + 16 + i * 0x13C)
            y = self.mem.read_xor_value(0x005991F8 + 32 + i * 0x13C)
            level = self.mem.read_int(0x005991F8 + 44 + i * 0x13C)
            count = self.mem.read_int(0x005991F8 + 80 + i * 0x13C)
            name = self.mem.read_string(0x005991F8 + 84 + i * 0x13C, 17)
            nick_name = self.mem.read_string(0x005991F8 + 101 + i * 0x13C, 17)
            title = self.mem.read_string(0x005991F8 + 184 + i * 0x13C, 17)
            item_name = self.mem.read_string(0x005991F8 + 201 + i * 0x13C, 67)
            flag = self.mem.read_short(0x005991F8 + 276 + i * 0x13C)
            injury = self.mem.read_int(0x005991F8 + 288 + i * 0x13C)

            unit = MapUnit(
                valid,
                type,
                id,
                model_id,
                (x, y),
                level,
                count,
                name,
                nick_name,
                title,
                item_name,
                flag,
                injury,
            )
            yield unit


class Map(InterfaceBase):

    def __init__(self, mem: CgMem):
        super().__init__(mem)
        self.units = MapUnitCollection(mem)
        self._map_files_cache = {}
        self._last_start = None
        self._last_searched_path = []
        self._last_map_id = 0
        self._search_counter = 0
        self._last_file: MapFile = None
        self._last_dest = None
        self._last_request_time = 0

    @property
    def enum(self):
        for map_enum in MapEnum:
            if self.id == map_enum.value:
                return map_enum
        return None

    @property
    def location(self):
        return (self.x, self.y)

    @property
    def x(self):
        return round(self.mem.read_float(0x00BF6CE8) / 64)

    @property
    def y(self):
        return round(self.mem.read_float(0x00BF6CE4) / 64)

    @property
    def x_62(self):
        return b62(self.x)

    @property
    def y_62(self):
        return b62(self.y)

    @property
    def id(self):
        return self.mem.read_int(0x00970430)

    @property
    def name(self):
        return self.mem.read_string(0x0095C870)

    @property
    def _path(self):
        """example return map\\0\\11015.dat"""

        path = self.mem.read_string(0x0018CCCC, encoding="UTF-8")
        if "map" not in path:
            path = self.mem.read_string(0x0018CCCC - 4, encoding="UTF-8")
        if "map" not in path:
            return ""
        directory = self.mem.read_string(0x00FF7D80, encoding="UTF-8").replace(
            "bluecg.exe", ""
        )
        return directory + path

    @property
    def file(self) -> MapFile:
        path = self._path

        if self._last_file and path == self._last_file.path:
            return self._last_file

        if path in self._map_files_cache:
            self._last_file = self._map_files_cache[path]
        else:
            self._last_file = MapFile(path)
            if not self._last_file.is_dungeon:
                self._map_files_cache[path] = self._last_file

        return self._last_file

    def find_transports(self, count=2):
        """如果找到的出入口小于count，会请求和读取地图数据"""
        if not self.file.is_full_downloaded or len(self.file.transports) < count:
            logging.debug("find transports, request and read")
            self.request_download()
            self.file.read()
        return self.file.transports

    def search(self, x: int | tuple, y: int = None) -> list[tuple[int, int]] | None:
        """
        未找到路径会自动调用self.request_download() 和 self.file.read()
        """
        destination = x if y is None else (x, y)
        start = self.location
        map_id = self.id

        # 使用缓存结果
        if (
            self._search_counter < 30
            and map_id == self._last_map_id
            and destination == self._last_dest
        ):
            # 起点相同
            if start == self._last_start:
                path = self._last_searched_path
            # 起点在上次搜索路径中
            elif start in self._last_searched_path:
                index = self._last_searched_path.index(start)
                path = self._last_searched_path[index + 1 :]
            else:
                path = None

            if path:
                merged_path = merge_path(path, start)
                self._search_counter += 1
                return merged_path

        self._search_counter = 0

        # 重新计算路径
        logging.debug(
            f"Search map:{map_id} start:{start} dest:{destination},last:{self._last_map_id},{self._last_start},{self._last_dest}"
        )
        path = a_star_search(self.file.flag_data, start, destination)
        if path:
            self._last_start = start
            self._last_dest = destination
            self._last_map_id = map_id
            self._last_searched_path = path
            merged_path = merge_path(path, start)
            return merged_path

        logging.debug("Search not found path! request_download and read")
        self.request_download()
        self.file.read()
        return []

    def request_download(self):
        """
        向服务器发送地图数据请求，地图后续更新需要一定时间 \n
        5秒之内最多执行一次，仅在迷宫中使用
        """
        if not self.file.is_dungeon:
            return
        if time.time() - self._last_request_time < 5:
            return
        size = 45
        e_start = self.file.width_east // size
        s_start = self.file.height_south // size
        for i in range(e_start + 1):
            for j in range(s_start + 1):
                self.mem.decode_send(
                    f"UUN 1 {b62(self.id)} {b62(i*size)} {b62(j*size)} {b62(i*size+size)} {b62(j*size+size)}"
                )
                time.sleep(0.2)
        self._last_request_time = time.time()

    def distance_to(self, x: int | tuple, y: int = None):
        if y is None:
            x, y = x
        return abs(self.x - x) + abs(self.y - y)

    def at(self, map_name: Literal["起始之地", "普雷德島", "多拉洞"]):
        return self.id == 1000

    def within(self, x1, y1, x2, y2=None):
        """判断坐标在一定范围内，左下到右上，如果y2为None则x2为半径"""
        if y2 is None:
            radius = x2
            return abs(self.x - x1) <= radius and abs(self.y - y1) <= radius

        return x1 <= self.x <= x2 and y1 <= self.y <= y2

    @property
    def in_city(self):
        return self.id in [1000, 30010, 1164]

    @property
    def in_hospital(self):
        return self.id in [1111, 1112, 30105]


class MapEnum(Enum):
    法兰城 = 1000
    职业公会 = 1092
    亚诺曼城 = 30010
    冒险者旅馆二楼 = 1164
    东医 = 1112
    西医 = 1111
    亚诺曼医院 = 30105


# 芙蕾雅	100
# 巴洛斯|12	101
# 索奇亚	300
# 阿卡斯	301
# 契约的海道	302
# 莎莲娜	400
# 佛利波罗	401
# 莎莲娜	402
# 法兰城	1000
# 希洛克武器店|0	1011
# 强盖鲁特武器店|0	1012
# 尼莫克防具店|0	1021
# 哈利防具店|0	1022
# 凯蒂夫人的店|0	1031
# 达美姊妹的店|0	1041
# 强哥杂货店|0	1051
# 陶欧食品店|0	1061
# 拿潘食品店|0	1062
# 米克尔工房|0	1071
# 房屋仲介所|0	1081
# 职业介绍所|0	1091
# 职业公会|0	1092
# 科特利亚酒吧|0	1101
# 酒吧里面|0	1102
# 彩卷卖场|0	1103
# 客房|0	1104
# 客房|0	1105
# 医院|0	1111
# 医院|0	1112
# 银行|0	1121
# 葛利玛的家|0	1150
# 艾文蛋糕店|0	1151
# 毕夫鲁的家|0	1152
# 基尔的家|0	1153
# 冒险者旅馆|0	1154
# 山男的家|0	1155
# 贝蒂的家|0	1156
# 修理工波利的家|0	1157
# 修理工利贝亚的家|0	1158
# 里玲香料店|0	1159
# 魔女之家|0	1160
# 毕安札的家|0	1161
# 流行商店|0	1162
# 冒险者旅馆	1164
# 水晶交换所|0	1165
# 冒险者旅馆	1166
# 安其摩酒吧|0	1170
# 酒吧里面|0	1171
# 客房|0	1172
# 彩券卖场|0	1174
# 宠物店|0	1180
# 弓箭手公会|0	1181
# 民家|0	1182
# 旅馆|0	1183
# 旅馆2楼|0	1184
# 希利布的家|0	1185
# 民家|0	1186
# 公寓|0	1187
# 公寓2楼|0	1188
# 美容院|0	1189
# 民家|0	1190
# 研究家真中的家|0	1191
# 民家|0	1192
# 豪宅|0	1193
# 豪宅|0	1194
# 王宫食堂|0	1195
# 大圣堂的入口|0	1201
# 礼拜堂|0	1202
# 通往地下楼梯的房间|0	1203
# 地下仓库|0	1204
# 后台|0	1205
# 2楼客房|0	1206
# 大圣堂里面|0	1207
# 大圣堂里面|0	1208
# 剧院	1301
# 剧院	1302
# 往后台的走廊|0	1303
# 后台|0	1304
# 后台|0	1305
# 竞技场的入口|0	1400
# 中央大厅|0	1401
# 后台|0	1402
# 治愈的广场|0	1403
# 休息室|0	1404
# 竞技场的迷宫|0	1405
# 第一名的房间|0	1406
# 第二名的房间|0	1407
# 第三名的房间|0	1408
# 第四名的房间|0	1409
# 第五名的房间|0	1410
# 第六名以后的房间|0	1411
# 竞技场的迷宫|0	1412
# 竞技场的迷宫|0	1413
# 升官图房间2|0	1420
# 升官图房间2|0	1421
# 升官图|0	1422
# 升官图导览间|0	1423
# 升官图走廊|0	1424
# 竞技场|0	1450
# 竞技场|0	1451
# 竞技场|0	1452
# 竞技场|0	1453
# 竞技场|0	1454
# 竞技场|0	1455
# 休息室|0	1456
# 竞技预赛会场|0	1457
# 竞技场|0	1458
# 竞技场|0	1459
# 竞技场|0	1460
# 竞技场|0	1461
# 竞技场|0	1462
# 竞技场|0	1463
# 竞技场|0	1464
# 竞技场|0	1465
# 竞技场|0	1466
# 竞技场|0	1467
# 竞技场|0	1468
# 竞技场|0	1469
# 竞技场|0	1470
# 竞技场|0	1471
# 竞技场|0	1472
# 竞技场|0	1473
# 竞技场|0	1474
# 竞技场|0	1475
# 竞技场|0	1476
# 竞技场|0	1477
# 竞技场|0	1478
# 竞技场|0	1479
# 竞技场|0	1480
# 竞技场|0	1481
# 休息室|0	1482
# 休息室|0	1483
# 休息室|0	1484
# 休息室|0	1485
# 休息室|0	1486
# 休息室|0	1487
# 休息室|0	1488
# 休息室|0	1489
# 休息室|0	1490
# 休息室|0	1491
# 休息室|0	1492
# 休息室|0	1493
# 休息室|0	1494
# 休息室|0	1495
# 休息室|0	1496
# 里谢里雅堡	1500
# 厨房|0	1502
# 图书室|0	1504
# 食堂|0	1506
# 客房|0	1507
# 客房|0	1508
# 客房|0	1509
# 客房|0	1510
# 谒见之间|0	1511
# 寝室|0	1512
# 走廊|0	1518
# 里谢里雅堡	1520
# 里谢里雅堡	1521
# 启程之间|0	1522
# 召唤之间|5	1530
# 回廊|5	1531
# 召唤之间|5	1533
# 召唤之间|5	1534
# 召唤之间|5	1535
# 召唤之间|5	1536
# 召唤之间|5	1537
# 封印之间|5	1538
# 宠物管理处|0	1539
# 中型屋|0	1540
# 豪华屋|0	1541
# 国民屋|0	1542
# 空屋出租|0	1800
# 空屋出租|0	1801
# 空屋出租|0	1802
# 空屋出租|0	1803
# 空屋出租|0	1804
# 空屋出租|0	1805
# 空屋出租|0	1806
# 空屋出租|0	1807
# 空屋出租|0	1808
# 空屋出租|0	1809
# 饲养师之家|0	1810
# 别室|0	1811
# 公寓|0	1850
# 公寓|0	1860
# 公寓|0	1870
# 伊尔村	2000
# 装备店|0	2001
# 旧金山|0	2002
# 医院|0	2010
# 村长的家|0	2012
# 泰勒的家|0	2013
# 巴侬的家|0	2014
# 伊尔村的传送点|0	2099
# 维诺亚村	2100
# 装备品店|0	2101
# 医院|0	2110
# 医院2楼|0	2111
# 村长的家|0	2112
# 村长的家|0	2113
# 荷特尔咖哩店|0	2120
# 民家|0	2121
# 村长家的小房间|0	2198
# 维诺亚村的传送点|0	2199
# 乌克兰	2200
# 杂货店|0	2201
# 杂货店	2202
# 医院|0	2211
# 村长的家|0	2212
# 族长的家地下室|12	2213
# 族长的家地下室|12	2214
# 地下室|12	2215
# 族长的家地下室|12	2216
# 民家|0	2220
# 梅兹的家|0	2221
# 小助的家|0	2223
# 小助的家|0	2224
# 小助的家|0	2225
# 小助的家|0	2226
# 小助的家|0	2250
# 小助的家|0	2251
# 小助的家|0	2252
# 小助的家|0	2253
# 小助的家|0	2254
# 小助的家|0	2255
# 小助的家|0	2256
# 小助的家|0	2257
# 小助的家|0	2258
# 小助的家|0	2259
# 小助的家|0	2260
# 圣拉鲁卡村	2300
# 装备品店|0	2301
# 1楼小房间|0	2302
# 地下工房|0	2303
# 食品店|0	2306
# 原料店|0	2307
# 赛杰利亚酒吧|0	2308
# 赛杰利亚酒吧|0	2309
# 医院|0	2310
# 医院	2311
# 村长的家|0	2312
# 村长的家	2313
# 民家|0	2320
# 圣拉鲁卡村的传送点|0	2399
# 亚留特村	2400
# 杂货店|0	2401
# 医院|0	2410
# 村长的家|0	2412
# 民家|0	2420
# 南希的家|0	2421
# 月亮俱乐部|1	2431
# 地下通路|2	2432
# 珍妮专用休息室|1	2433
# 亚留特村的传送点|0	2499
# 民家|0	2800
# 民家|0	2801
# 民家|0	2802
# 民家|0	2803
# 民家|0	2804
# 民家|0	2805
# 民家|0	2806
# 民家|0	2807
# 民家|0	2808
# 加纳村	3000
# 装备品店|0	3001
# 杂货店|0	3002
# 酒吧|0	3008
# 医院|0	3010
# 村长的家|0	3012
# 村长的家|0	3013
# 村长的家|0	3014
# 考古学者之家|0	3020
# 传承者之家|0	3021
# 加纳村的传送点|0	3099
# 哈贝鲁村|0	3100
# 奇利村	3200
# 装备品店|0	3201
# 杂货店|0	3202
# 酒吧|0	3208
# 医院|0	3210
# 村长的家|0	3212
# 村长的家|0	3213
# 村长的家|0	3214
# 民家|0	3220
# 老夫妇的家|0	3221
# 奇利村的传送点|0	3299
# 没落的村庄	3300
# 连接时空的房间|2	3301
# 冯奴的家|0	3350
# 冯奴的家|0	3351
# 冯奴的家|0	3352
# 冯奴的家|0	3353
# 冯奴的家|0	3354
# 砂尘洞穴|12	3355
# 民家|0	3801
# 民家|0	3802
# 民家|0	3803
# 民家|0	3804
# 民家|0	3805
# 民家|0	3806
# 民家|0	3807
# 杰诺瓦镇	4000
# 杂货店|0	4001
# 装备品店|0	4002
# 酒吧|0	4008
# 酒吧的地下室|0	4009
# 医院|0	4010
# 医院2楼|0	4011
# 村长的家|0	4012
# 村长的家|0	4013
# 民家|0	4020
# 客房|0	4021
# 客房|0	4022
# 杰诺瓦镇的传送点|0	4099
# 阿斯提亚镇	4100
# 神殿|0	4130
# 众神之墓|0	4131
# 回复之间|0	4140
# 神殿|0	4141
# 大厅|0	4142
# 神殿|0	4143
# 神殿|0	4144
# 神殿|0	4145
# 神殿|0	4146
# 蒂娜村	4200
# 蒂娜村|2	4201
# 食品材料店|0	4206
# 酒吧|0	4208
# 酒吧的地下室|0	4209
# 医院|0	4210
# 医院|0	4211
# 村长的家|0	4212
# 村长的家|0	4213
# 村长的家|0	4214
# 民家|0	4220
# 酒吧的地下室|0	4221
# 酒吧的地下室|0	4222
# 酒吧|0	4230
# 蒂娜村的传送点|0	4232
# 蒂娜村的传送点|0	4299
# 阿巴尼斯村	4300
# 酒吧|0	4308
# 酒吧的地下室|0	4309
# 医院|0	4310
# 村长的家|0	4312
# 村长的家|0	4313
# 民家|0	4320
# 客房|0	4321
# 客房|0	4322
# 民家|0	4330
# 民家地下|0	4331
# 民家地下|14	4332
# 民家|14	4333
# 民家地下|14	4334
# 民家地下|0	4335
# 阿巴尼斯村的传送点|0	4399
# 魔法大学	4400
# 实验室|0	4401
# 地下实验室|0	4402
# 青龙的洞窟	4403
# 青龙的洞窟	4404
# 青龙的洞窟	4405
# 青龙的洞窟	4406
# 青龙的洞窟	4408
# 青龙之巢|0	4409
# 魔法大学内部|0	4410
# 技术室|0	4411
# 更衣室|0	4412
# 调理室|0	4413
# 教室|0	4414
# 教室|0	4415
# 教师室|0	4416
# 音乐室|0	4417
# 礼堂|0	4418
# 学长室|0	4419
# 保健室|0	4420
# 合格房间|0	4421
# 家畜小屋|0	4422
# 家畜小屋|0	4423
# 家畜小屋|0	4424
# 实验室|0	4430
# 音乐室|13	4431
# 音乐室|2	4432
# 仓库内部|0	4451
# 仓库内部|0	4452
# 仓库内部|0	4453
# 仓库内部|0	4454
# 仓库内部|0	4455
# 地底湖	4456
# 地底湖	4457
# 废屋|6	4500
# 被封闭的祭坛|0	4501
# 被封闭的祭坛|0	4502
# 民家|0	4800
# 民家|0	4801
# 民家|0	4802
# 民家|0	4803
# 民家|0	4804
# 民家|0	4805
# 民家|0	4806
# 民家|0	4807
# 民家|0	4808
# 民家|0	4809
# 民家|0	4810
# 民家|0	4811
# 民家|0	4812
# 哥布林镇|0	5000
# 大地鼠婆婆之家|0	5001
# 大地鼠婆婆之家|0	5002
# 饲养师训练所|0	5003
# 启程之间	5004
# 井的底部|6	5005
# 希尔薇亚的家|0	5006
# 民家|0	5007
# 香蒂的房间|0	5008
# 香蒂的房间|0	5009
# 香蒂的房间|0	5010
# 香蒂的房间|0	5011
# 香蒂的房间|0	5012
# 香蒂的房间|0	5013
# 香蒂的房间|0	5014
# 龙之住处|10	5015
# 黄金之洞窟	5016
# 伊尔村	6100
# 维诺亚村	6200
# 乌克兰	6300
# 圣拉鲁卡村	6400
# 亚留特村	6500

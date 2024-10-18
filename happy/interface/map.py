import os
import struct
import pickle
import time
import csv
import logging
import hashlib
from happy.interface.mem import CgMem, InterfaceBase
from happy.util.path_search import merge_path, a_star_search
from happy.util import b62, log_execution_time
from threading import Lock


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
            self._search_counter < 50
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

    def in_area(self, x1, y1, x2, y2=None):
        """左()下到右上，如果y2为None则x2为半径"""
        if y2 is None:
            radius = x2
            return abs(self.x - x1) <= radius and abs(self.y - y1) <= radius

        return x1 <= self.x <= x2 and y1 <= self.y <= y2

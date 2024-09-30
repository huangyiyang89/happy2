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


    def hash(self):
        md5 = hashlib.md5()
        try:
            with open(self.path, 'rb') as file:
                data = file.read()
                md5.update(data)
            return md5.hexdigest()
        except FileNotFoundError:
            logging.warning(f"文件 {self.path} 不存在。")
            return ""

    @property
    def transports(self):
        return self._transports

    @property
    def is_full_downloaded(self):
        return self._is_full_downloaded

    @property
    def is_dungeon(self):
        return "map\\1\\" in self.path 

    @property
    def _pickle_path(self):
        """example data\\map\\0\\1530.dat"""
        return "data\\map\\" + self.path.split("map\\")[1]

    def dunp_flag_data_to_csv(self):
        with open(self._pickle_path + ".csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            for row in self._flag_data:
                writer.writerow(row)

    def dump_flag_data(self):
        if not self._flag_data:
            return
        
        directory = os.path.dirname(self._pickle_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(self._pickle_path, "wb") as f:
            pickle.dump(self._flag_data, f)
            logging.debug(f"Dump map flag data to {self._pickle_path}")

        
    def load_flag_data(self):
        try:
            with open(self._pickle_path, "rb") as f:
                self._flag_data = pickle.load(f)
        except FileNotFoundError:
            print(f"load_flag_data 文件 {self._pickle_path} 不存在。")
        except pickle.UnpicklingError as e:
            print(f"反序列化文件 {self._pickle_path} 时出现错误：{e}")
        except Exception as e:
            print(f"发生未知错误：{e}")

    @log_execution_time(0.1)
    def read(self):
        """self.flag_data[x][y] 1表示有障碍，0表示可通过，读取失败self.flag_data=[]"""

        hash = self.hash()
        if self._last_hash == hash :
            logging.debug(f"{self.path} READ MD5一致 使用缓存")
            return self._flag_data
        
        logging.debug(f"READ {self.path}")
        self._last_hash = hash
        full_downloaded = True

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

                        
                        if  flag == 0 :
                            full_downloaded = False

                        # flag == 49162是出口切换地图 49155是水晶传送上下楼梯 49152正常通过 49154遭遇战斗 0为未探索
                        if flag == 49155:
                            self._transports.append((j, i, object_id))

                        if (
                            flag != 49162
                            and flag != 49155
                            and flag != 49152
                            and flag != 49154
                            and flag != 0
                        ):
                            logging.error("flag 未找到")

                        # 地上不可通过物件
                        if object_id in _object_dict:
                            e, s = _object_dict[object_id]
                            for l in range(s):
                                for m in range(e):
                                    self._flag_data[i - l][j + m] = 1
        
            self._is_full_downloaded = full_downloaded

    
        except FileNotFoundError:
            logging.warning(f"文件 {self.path} 不存在。")
        except Exception as e:
            logging.error(f"文件 {e} 读取失败。")
        finally:
            return self._flag_data

    @property
    def flag_data(self):
        if not self.is_dungeon:
            if not self._flag_data:
                self.load_flag_data()
            if not self._flag_data:
                self.read()
                self.dump_flag_data()
        return self._flag_data


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
        self._last_path = []
        self._last_map_id = 0
        self._last_dest = None

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
        if path in self._map_files_cache:
            return self._map_files_cache[path]

        file = MapFile(path)
        self._map_files_cache[path] = file
        return file


    def find_transports(self):
        
        if not self.file.is_full_downloaded:
            logging.debug("find transports request and read")
            self.request_download()
            self.file.read()        
        return self.file.transports


    @log_execution_time(0.1)
    def search(self, x: int | tuple, y: int = None) -> list[tuple[int, int]] | None:

        if y is None:
            destination = x
        else:
            destination = (x, y)

        start = self.location

        # 使用缓存结果
        # 参数完全相同，直接使用上次结果
        if (
            start == self._last_start
            and self.id == self._last_map_id
            and destination == self._last_dest
        ):
            path = self._last_path
            merged_path = merge_path(path, start)
            return merged_path
        
        # 当前起点在上次路径中
        if (
            start in self._last_path
            and self.id == self._last_map_id
            and destination == self._last_dest
        ):
            index = self._last_path.index(start)
            path = self._last_path[index + 1 :]
            merged_path = merge_path(path, start)
            return merged_path

        #无数据直接返回空
        if not self.file.flag_data:
            return None

        # 重新计算路径
        logging.debug(f"Search map:{self.id} start:{start} dest:{destination},last:{self._last_map_id},{self._last_start},{self._last_dest}")
        path = a_star_search(self.file.flag_data, start, destination)
        if path:
            self._last_start = start
            self._last_dest = destination
            self._last_map_id = self.id
            self._last_path = path
            merged_path = merge_path(path, start)
            return merged_path
        logging.info(f"Search, NOT FOUND:{self.id} start:{start} dest:{destination}")
        return None

    def request_download(self):
        size = 45
        e_start = self.file.width_east // size
        s_start = self.file.height_south // size
        for i in range(e_start + 1):
            for j in range(s_start + 1):
                self.mem.decode_send(
                    f"UUN 1 {b62(self.id)} {b62(i*size)} {b62(j*size)} {b62(i*size+size)} {b62(j*size+size)}"
                )
                time.sleep(0.1)
        time.sleep(1)

    def distance_to(self, x: int | tuple, y: int = None):
        if y is None:
            x, y = x
        return abs(self.x - x) + abs(self.y - y)

import time
import logging
import pymem
import pymem.process
from happy.util import b62

def find_all_cg_process_id(process_name=b"bluecg.exe"):
    """find all processes
    Args:
        process_name (bytes, optional): process name. Defaults to b"bluecg.exe".
    Yields:
        ProcessEntry32:(dwFlags,th32ProcessID)
    """
    cg_list = pymem.process.list_processes()
    for process in cg_list:
        if process.szExeFile == process_name:
            yield process.th32ProcessID

class CgMem(pymem.Pymem):

    def read_string(self, address, byte=50, encoding="big5", end=b"\x00"):
        """_summary_

        Args:
            address (_type_): _description_
            byte (int, optional): _description_. Defaults to 50.
            encoding (str, optional): _description_. Defaults to "big5".
            end (bytes, optional): _description_. Defaults to b"\x00".

        Returns:
            _type_: _description_
        """
        buff = self.read_bytes(address, byte)
        i = buff.find(end)
        if i != -1:
            buff = buff[:i]
        buff = buff.decode(encoding, errors="replace")
        return buff

    def read_xor_value(self, address) -> int:
        """_summary_

        Args:
            address (_type_): _description_

        Returns:
            _type_: _description_
        """
        x = self.read_int(address)
        y = self.read_int(address + 4)
        return x ^ y

    def decode_send(self, content):
        """发明文包"""
        # 0057E998 客户端随机数，找到写入注释掉
        # 说话call 00507780
        # 0050D3C9 打断点 看ecx地址 是指令字符串
        # 0050D2D0 打断点 看指针0057A718是完整加密字符串

        # jump hook
        self.write_int(0x00507780, 0x0799CBE9)
        # 汇编指令写入
        self.write_bytes(
            0x00581150,
            bytes.fromhex(
                "FF 25 D0 11 58 00 8B 05 00 10 58 00 A3 40 11 58 00 C7 \
                05 44 11 58 00 00 00 00 00 68 40 11 58 00 68 40 11 \
                58 00 E8 E6 C1 F8 FF 83 C4 08 B8 00 10 58 00 8B \
                0D 40 11 58 00 80 3D 02 10 58 00 20 66 89 08 \
                74 12 80 3D 03 10 58 00 20 89 08 75 07 C6 05 03 10 \
                58 00 20 8B 54 24 10 50 52 E8 1F C1 F8 FF 83 C4 08 C7 05 \
                D0 11 58 00 C0 11 58 00 C3 90 8B 05 18 A7 57 00 E9 BA 65 \
                F8 FF 90 90 90 90 90 56 11 58 00"
            ),
            132,
        )

        self.write_string(0x00581000, content + " \0")

        # 触发说话
        # 聊天栏字符长度
        self.write_int(0x00613904, 1)
        # 回车
        self.write_int(0x0072BD15, 26)
        # 延迟防止不触发
        time.sleep(0.2)
        account = self.read_string(0x00D15644)
        logging.debug(f"{account}, decode_send: "+content)

    def close_handle(self):
        # jump hook
        self.write_int(0x00507780, 0x0799CBE9)
        # 汇编指令写入
        self.write_bytes(
            0x00581150,
            bytes.fromhex(
                "FF 25 D0 11 58 00 8B 05 7C 8A 92 00 83 E8 04 50 FF 15 24 E1 53 00 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 C7 05 D0 11 58 00 C0 11 58 00 C3 90 8B 05 18 A7 57 00 E9 BA 65 F8 FF 90 90 90 90 90 56 11 58 00"
            ),
            132,
        )
        # 触发说话
        # 聊天栏字符长度
        self.write_int(0x00613904, 1)
        # 回车
        self.write_int(0x0072BD15, 26)
        # 延迟防止不触发
        time.sleep(0.2)

class InterfaceBase:
    def __init__(self, mem: CgMem):
        self.mem = mem

class LocationBase(InterfaceBase):
    @property
    def _x(self):
        return int(self.mem.read_float(0x00BF6CE8) / 64)

    @property
    def _y(self):
        return int(self.mem.read_float(0x00BF6CE4) / 64)

    @property
    def _x_62(self):
        return b62(self._x)

    @property
    def _y_62(self):
        return b62(self._y)

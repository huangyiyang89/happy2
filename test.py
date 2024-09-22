import os
import logging
import happy
import time
from happy.util import b62
logging.basicConfig(
    # filename="unhappy.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

cg = happy.open("mlbbdd01")


def clear_screen():
    """清屏函数"""
    # 对于Windows系统
    if os.name == "nt":
        os.system("cls")
    # 对于Mac和Linux系统
    else:
        os.system("clear")

while True:
    for unit in list(cg.battle.units.friends):
        print(unit.name,unit.position,unit.unknown3,unit.unknown9,unit.unknown10,unit.unknown11)
    time.sleep(1)
    clear_screen()

#cg.mem.decode_send(f"UUN 1 {b62(cg.map.id)} {b62(25)} {b62(15)} {b62(50)} {b62(40)}")
# injury 4096 店铺

# 玩家 type == 8 and flag = 256
# 物品 type == 2 and flag = 1024
# 留言板 type == 17 flag == 4096
# NPC type == 1 flag == 4096
# 宠物 type == 1 flag == 512
# 金币 type ==4 flag ==2048

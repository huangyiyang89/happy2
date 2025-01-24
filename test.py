import os
import logging
import happy
import time
import hashlib
from happy.util import b62

logging.basicConfig(
    filename="unhappy.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def clear_screen():
    """清屏函数"""
    # 对于Windows系统
    if os.name == "nt":
        os.system("cls")
    # 对于Mac和Linux系统
    else:
        os.system("clear")



cg = happy.open("freyahuang05")

if cg.battle.is_player_turn:
    cg.battle.player.use_item()
#wD
# cg.mem.decode_send(f"zA {b62(433)} {b62(263)} d 0")
# cg.mem.decode_send(f"zA {b62(435)} {b62(265)} 5 0")
# cg.mem.decode_send(f"zA {b62(435)} {b62(265)} c 0")
#cg.request("4","5g",unit.id)
#cg.mem.decode_send(f"zA {b62(431)} {b62(260)} dd 0")

#cg.mem.decode_send(f"zA {b62(435)} {b62(265)} cc 0")


# cg.mem.decode_send(f"UUN 1 {b62(cg.map.id)} {b62(25)} {b62(15)} {b62(50)} {b62(40)}")
# injury 4096 店铺

# 玩家 type == 8 and flag = 256
# 物品 type == 2 and flag = 1024
# 留言板 type == 17 flag == 4096
# NPC type == 1 flag == 4096
# 宠物 type == 1 flag == 512
# 金币 type ==4 flag ==2048





import happy
import time


cg = happy.open("mlbbdd01")

#cg.close_all_window()



#cg.interact("xF n k 7NT 6tb 4 1 ")
pointer = cg.mem.read_int(0x0057A718)
last_data = None
last_content = None
last_seller = None
last_map = None

last_recv = None

while True:
    # data = cg.mem.read_string(pointer,encoding="utf-8")
    # content = cg.dialog.content
    # seller = cg.mem.read_string(0x00C43BF4)
    # request_map = cg.mem.read_string(0x0018D5FD)

    recv = cg.mem.read_string(0x00D04EA0)
    if recv and recv!=last_recv:
        print(recv)
        last_recv = recv

    # if data and data!= last_data:
    #     print(data.replace("\n",""))
    #     last_data = data
    
    # if content and content!=last_content:
    #     #print(content.replace("\n",""))
    #     last_content = content

    # if seller and seller!=last_seller:
    #     #print(seller.replace("\n",""))
    #     last_seller = seller
    
    # if request_map and request_map!=last_map:
    #     if "UWL" in request_map:
    #         cg.map.file.read()
    #         print(cg.map.file.width_east,cg.map.file.height_south)
    #         print(cg.map.x_62,cg.map.y_62)
    #         print(request_map)
    #         last_map = request_map

    


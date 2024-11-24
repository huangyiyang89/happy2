import win32gui
import win32process

class Window:
    def __init__(self, pid):
        self.pid = pid
        self.hwnd = self.get_hwnd()

    def get_hwnd(self):
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == self.pid:
                    hwnds.append(hwnd)
            return True

        hwnds = []
        win32gui.EnumWindows(callback, hwnds)

        if hwnds:
            return hwnds[0]
        else:
            print(f"未找到PID为 {self.pid} 的进程的主窗口。")
            return None

    def move_to(self, x, y):
        if self.hwnd:
            win32gui.MoveWindow(self.hwnd, x, y, 0, 0, True)
        else:
            print("无法移动窗口，因为未找到对应的窗口句柄。")

    def move_to_slot(self, slot, count_per_row=3):
        slot = slot - 1
        row = slot // count_per_row
        column = slot % count_per_row
        self.move_to(427*column, 343*row)

    def __str__(self):
        return f"Window(pid={self.pid}, hwnd={self.hwnd})"

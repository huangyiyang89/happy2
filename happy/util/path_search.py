import heapq

DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

class Node:
    def __init__(self, x, y, cost, heuristic, parent=None):
        self.x = x
        self.y = y
        self.cost = cost  # g(n): 从起点到该节点的实际代价
        self.heuristic = heuristic  # h(n): 启发式估计
        self.parent: Node | None = parent  # 父节点，用于路径回溯

    @property
    def total_cost(self):
        return self.cost + self.heuristic  # f(n) = g(n) + h(n)

    def __lt__(self, other:"Node"):
        return self.total_cost < other.total_cost

def a_star_search(grid, start, goal):
    if not grid:
        return None

    start_node = Node(start[0], start[1], 0, heuristic_euclid(start, goal))
    goal_node = Node(goal[0], goal[1], 0, 0)

    open_list = []
    heapq.heappush(open_list, start_node)
    closed_set = set()

    while open_list:
        current_node: Node = heapq.heappop(open_list)

        if (current_node.x, current_node.y) in closed_set:
            continue

        closed_set.add((current_node.x, current_node.y))

        # 如果到达目标节点，则回溯路径
        if (current_node.x, current_node.y) == (goal_node.x, goal_node.y):
            path = reconstruct_path(current_node)
            return path

        # 遍历8个方向的邻居节点
        for direction in DIRECTIONS:
            new_x, new_y = current_node.x + direction[0], current_node.y + direction[1]

            if not is_valid_move(grid, new_x, new_y):
                continue

            # 如果是斜向移动，确保横竖方向均可移动
            if abs(direction[0]) == 1 and abs(direction[1]) == 1:
                if not (
                    is_valid_move(grid, current_node.x, new_y)
                    and is_valid_move(grid, new_x, current_node.y)
                ):
                    continue
                new_cost = current_node.cost + 1.4
            else:
                new_cost = current_node.cost + 1
            heuristic_value = heuristic_euclid((new_x, new_y), goal)
            neighbor_node = Node(new_x, new_y, new_cost, heuristic_value, current_node)

            if (new_x, new_y) not in closed_set:
                heapq.heappush(open_list, neighbor_node)

    return None

def is_valid_move(grid, x, y):
    # 检查 (x, y) 是否在地图范围内，且该位置可通行
    return 0 <= x < len(grid[0]) and 0 <= y < len(grid) and grid[y][x] == 0

def heuristic_manhattan(pos, goal):
    """曼哈顿距离启发式函数"""
    return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

def heuristic_euclid(pos, goal):
    """欧几里得距离启发函数"""
    hx = pos[0] - goal[0]
    hy = pos[1] - goal[1]
    return (hx ** 2 + hy ** 2) ** 0.5

def reconstruct_path(current: Node):
    path = []
    node = current
    while node.parent is not None:
        path.append((node.x, node.y))
        node = node.parent
    return path[::-1]

def merge_path(paths, start):
    if len(paths) < 3:
        return paths  # 如果路径点数少于3，只返回终点

    # 初始化简化后的路径（不包含起点）
    merged_path = []

    # 遍历路径的每个点，尝试简化路径
    for i in range(0, len(paths) - 2):
        A = (
            start if not merged_path else merged_path[-1]
        )  # 上一个已简化的点（起点或路径中的最后一个点）
        B = paths[i]  # 当前点
        C = paths[i + 1]  # 下一个点

        # 如果三点不在同一条直线上，将当前点 B 添加到简化路径中
        if not (B[1] - A[1]) * (C[0] - B[0]) == (C[1] - B[1]) * (B[0] - A[0]):
            merged_path.append(B)

    # 添加最后两个点
    merged_path.append(paths[-2])
    merged_path.append(paths[-1])

    return merged_path

import numpy as np
from gurobipy import *
import matplotlib.pyplot as plt


class VRPTWSolver:
    def __init__(self, coordinates, demands, time_windows, service_times, capacity, num_vehicles, depot=0):
        """
        初始化VRPTW求解器

        Parameters:
            coordinates: List[tuple], 节点坐标列表 [(x1,y1), (x2,y2),...]
            demands: List[float], 各节点需求量
            time_windows: List[tuple], 时间窗列表 [(e1,l1), (e2,l2),...] (ei:最早时间, li:最晚时间)
            service_times: List[float], 各节点服务时间
            capacity: float, 车辆容量
            num_vehicles: int, 车辆数量
            depot: int, 仓库节点索引(默认为0)
        """
        self.coordinates = coordinates
        self.demands = demands
        self.time_windows = time_windows
        self.service_times = service_times
        self.capacity = capacity
        self.num_vehicles = num_vehicles
        self.depot = depot

        self.n = len(coordinates)  # 节点数量
        self.distances = self._calculate_distances()
        self.times = self.distances  # 假设行驶时间等于距离

        self.model = None
        self.x_vars = None  # 路径决策变量
        self.t_vars = None  # 到达时间变量
        self.solution = None

    def _calculate_distances(self):
        """计算节点间距离矩阵"""
        distances = np.zeros((self.n, self.n))
        for i in range(self.n):
            for j in range(self.n):
                if i != j:
                    x1, y1 = self.coordinates[i]
                    x2, y2 = self.coordinates[j]
                    distances[i][j] = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        return distances

    def build_model(self):
        """构建VRPTW数学模型"""
        # 创建模型
        self.model = Model("VRPTW")

        # 决策变量
        # x[i,j,k] = 1 表示车辆k从节点i到节点j
        self.x_vars = self.model.addVars(self.n, self.n, self.num_vehicles,vtype=GRB.BINARY, name="x")

        # t[i,k] t[i,k] 表示车辆k到达节点i的时间
        self.t_vars = self.model.addVars(self.n, self.num_vehicles,vtype=GRB.CONTINUOUS, name="t")

        # 目标函数：最小化总行驶距离
        obj = quicksum(self.distances[i, j] * self.x_vars[i, j, k]
                       for i in range(self.n) for j in range(self.n)
                       for k in range(self.num_vehicles) if i != j)
        self.model.setObjective(obj, GRB.MINIMIZE)

        # 约束条件

        # 1. 每个客户节点必须且只能被访问一次
        for j in range(1, self.n):  # 跳过仓库节点
            self.model.addConstr(quicksum(self.x_vars[i, j, k]
                                          for i in range(self.n) if i != j
                                          for k in range(self.num_vehicles)) == 1)

        # 2. 车辆流平衡约束
        for k in range(self.num_vehicles):
            for h in range(self.n):
                self.model.addConstr(
                    quicksum(self.x_vars[i, h, k] for i in range(self.n) if i != h) ==
                    quicksum(self.x_vars[h, j, k] for j in range(self.n) if j != h)
                )

        # 3. 所有车辆最多从仓库出发一次
        for k in range(self.num_vehicles):
            self.model.addConstr(
                quicksum(self.x_vars[self.depot, j, k]
                         for j in range(1, self.n)) <= 1)

        # 4. 容量约束
        for k in range(self.num_vehicles):
            self.model.addConstr(
                quicksum(self.demands[j] * quicksum(self.x_vars[i, j, k]
                                                    for i in range(self.n) if i != j)
                         for j in range(1, self.n)) <= self.capacity)

        # 5. 时间窗约束
        M = max(l for _, l in self.time_windows)  # 足够大的常数

        for k in range(self.num_vehicles):
            # 从仓库出发的时间
            self.model.addConstr(self.t_vars[self.depot, k] >=
                                 self.time_windows[self.depot][0])

            # 时间窗和时间连续性约束
            for i in range(self.n):
                # 时间窗约束
                self.model.addConstr(self.t_vars[i, k] >= self.time_windows[i][0])
                self.model.addConstr(self.t_vars[i, k] <= self.time_windows[i][1])

                # 时间连续性约束
                for j in range(1, self.n):
                    if i != j:
                        self.model.addConstr(
                            self.t_vars[i, k] + self.service_times[i] +
                            self.times[i, j] - M * (1 - self.x_vars[i, j, k]) <=
                            self.t_vars[j, k]
                        )

    def solve(self):
        """求解VRPTW模型"""
        if self.model is None:
            self.build_model()

        # 求解模型
        self.model.optimize()

        # 提取解
        if self.model.status == GRB.OPTIMAL:
            self.solution = []

            # 对每辆车提取路径
            for k in range(self.num_vehicles):
                route = []
                current = self.depot

                # 如果这辆车被使用（从仓库出发）
                if sum(self.x_vars[self.depot, j, k].x > 0.5 for j in range(self.n)) > 0: #至少有一个客户被这辆车服务
                    route.append(current)

                    # 继续寻找路径直到返回仓库
                    while True:
                        for j in range(self.n):
                            if current != j and self.x_vars[current, j, k].x > 0.5:
                                current = j
                                route.append(current)
                                break
                        if current == self.depot:
                            break

                    if len(route) > 2:  # 如果路径有效
                        self.solution.append({
                            'vehicle': k,
                            'route': route,
                            'times': [self.t_vars[i, k].x for i in route]
                        })
            return True
        return False

    def get_solution(self):
        """获取求解结果"""
        if self.solution is None:
            return None
        return self.solution

    def get_total_distance(self):
        """获取总距离"""
        if self.solution is None:
            return None
        total_distance = 0
        for route_info in self.solution:
            route = route_info['route']
            for i in range(len(route) - 1):
                total_distance += self.distances[route[i]][route[i + 1]]
        return total_distance

    def plot_solution(self):
        """可视化解"""
        if self.solution is None:
            print("No solution to plot")
            return

        plt.figure(figsize=(12, 8))

        # 绘制所有节点
        x = [self.coordinates[i][0] for i in range(self.n)]
        y = [self.coordinates[i][1] for i in range(self.n)]

        # 特别标注仓库
        plt.scatter(x[self.depot], y[self.depot], c='red', s=200, marker='*')
        plt.annotate(f'Depot', (x[self.depot], y[self.depot]))

        # 绘制客户节点
        plt.scatter(x[1:], y[1:], c='blue', s=50)
        for i in range(1, self.n):
            plt.annotate(f'C{i}', (x[i], y[i]))

        # 为每条路径使用不同的颜色
        colors = plt.cm.rainbow(np.linspace(0, 1, len(self.solution)))

        # 绘制路径
        for route_info, color in zip(self.solution, colors):
            route = route_info['route']
            for i in range(len(route) - 1):
                plt.plot([self.coordinates[route[i]][0],
                          self.coordinates[route[i + 1]][0]],
                         [self.coordinates[route[i]][1],
                          self.coordinates[route[i + 1]][1]],
                         c=color, linewidth=2)

        plt.title('VRPTW Solution')
        plt.grid(True)
        plt.show()



def read_solomon_instance(filename):
    """
    读取Solomon算例文件

    Parameters:
        filename: str, Solomon算例文件路径
    Returns:
        tuple: (coordinates, demands, time_windows, service_times, capacity, vehicle_num)
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    # 读取车辆数量和容量
    vehicle_info = lines[4].strip().split()
    num_vehicles = int(vehicle_info[0])
    capacity = int(vehicle_info[1])

    # 跳过头部信息
    data_start = 9

    coordinates = []
    demands = []
    time_windows = []
    service_times = []

    # 读取节点信息
    for line in lines[data_start:]:
        if line.strip():
            data = list(map(float, line.strip().split()))
            # Solomon格式：CUST NO.  XCOORD.   YCOORD.    DEMAND   READY TIME   DUE DATE   SERVICE TIME
            coordinates.append((data[1], data[2]))
            demands.append(data[3])
            time_windows.append((data[4], data[5]))
            service_times.append(data[6])

    return coordinates, demands, time_windows, service_times, capacity, num_vehicles


if __name__ == "__main__":
    # 读取Solomon算例
    instance_file = "data/solomon_100/C102.txt"  # Solomon算例文件路径

    try:
        # 读取算例数据
        coords, demands, time_windows, service_times, capacity, num_vehicles = read_solomon_instance(instance_file)

        print(f"实例信息:")
        print(f"节点数量: {len(coords)}")
        print(f"车辆数量: {num_vehicles}")
        print(f"车辆容量: {capacity}")

        # 创建求解器实例
        solver = VRPTWSolver(
            coordinates=coords,
            demands=demands,
            time_windows=time_windows,
            service_times=service_times,
            capacity=capacity,
            num_vehicles=num_vehicles,
            depot=0
        )
    except Exception as e:
        print(f"读取文件或创建求解器时出错：{e}")
        exit(1)


    if solver.solve():
        # 获取结果
        solution = solver.get_solution()
        total_distance = solver.get_total_distance()

        print("最优路径:")
        for route_info in solution:
            print(f"车辆 {route_info['vehicle']}: {route_info['route']}")
            print(f"到达时间: {[f'{t:.2f}' for t in route_info['times']]}")
        print(f"总距离: {total_distance:.2f}")

        # 可视化结果
        solver.plot_solution()
    else:
        print("未找到可行解")
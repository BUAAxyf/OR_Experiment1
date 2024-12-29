import gurobipy as gp
from gurobipy import GRB
import math


class Constraint:
    """
    约束类
    """
    def __init__(self, customer_data, x, load, vehicle_data, num_vehicles):
        self.customer_data = customer_data  # 客户数据
        self.x = x  # 决策变量
        self.load = load  # 负载
        self.vehicle_data = vehicle_data  # 车辆数据
        self.num_vehicles = num_vehicles  # 车辆数量
        self.n = len(customer_data)  # 客户数量

    def add_constraints(self, model):
        """
        添加约束
        :param model:
        :return:
        """
        # 1. 客户访问约束：每个客户必须且只能被访问一次
        for j in range(1, self.n):  # 跳过depot(0)
            model.addConstr(gp.quicksum(self.x[i, j, k]
                                        for i in range(self.n)
                                        for k in range(self.num_vehicles)) == 1,
                            f"visit_customer_{j}")

        # 2. 车辆流平衡约束
        # 2.1 每辆车必须从depot出发
        for k in range(self.num_vehicles):
            model.addConstr(gp.quicksum(self.x[0, j, k] for j in range(1, self.n)) <= 1,
                            f"depot_out_{k}")

        # 2.2 流入流出平衡：对于每个节点，进入的车辆数等于离开的车辆数
        for h in range(self.n):
            for k in range(self.num_vehicles):
                model.addConstr(
                    gp.quicksum(self.x[i, h, k] for i in range(self.n)) ==
                    gp.quicksum(self.x[h, j, k] for j in range(self.n)),
                    f"flow_balance_{h}_{k}")

        # 3. 容量约束
        # 3.1 初始化depot的负载
        for k in range(self.num_vehicles):
            model.addConstr(self.load[0, k] == 0, f"init_load_{k}")

        # 3.2 负载传播与容量限制
        for i in range(self.n):
            for j in range(1, self.n):  # j从1开始，跳过depot
                for k in range(self.num_vehicles):
                    M = self.vehicle_data['capacity']  # 大M
                    model.addConstr(
                        self.load[j, k] >= self.load[i, k] + self.customer_data[j]['demand'] - M * (1 - self.x[i, j, k]),
                        f"load_prop_{i}_{j}_{k}")

        # 3.3 确保不超过车辆容量
        for i in range(self.n):
            for k in range(self.num_vehicles):
                model.addConstr(
                    self.load[i, k] <= self.vehicle_data['capacity'],
                    f"capacity_{i}_{k}")

        # 4. 时间窗约束
        # 4.1 添加时间变量
        arrival_time = model.addVars(self.n, self.num_vehicles,
                                     vtype=GRB.CONTINUOUS, name="arrival_time")

        # 4.2 设置到达时间约束
        for i in range(self.n):
            for j in range(1, self.n):  # j从1开始，跳过depot
                for k in range(self.num_vehicles):
                    # 计算从i到j的行驶时间
                    travel_time = math.sqrt(
                        (self.customer_data[i]['x'] - self.customer_data[j]['x']) ** 2 +
                        (self.customer_data[i]['y'] - self.customer_data[j]['y']) ** 2
                    )

                    M = max(c['due_date'] for c in self.customer_data)  # Big-M值

                    # 如果车辆k从i到j，则考虑时间窗约束
                    model.addConstr(
                        arrival_time[j, k] >=
                        arrival_time[i, k] +
                        self.customer_data[i]['service_time'] +
                        travel_time -
                        M * (1 - self.x[i, j, k]),
                        f"time_window_prop_{i}_{j}_{k}")

        # 4.3 确保在时间窗内到达
        for i in range(1, self.n):  # 从1开始，跳过depot
            for k in range(self.num_vehicles):
                model.addConstr(
                    arrival_time[i, k] >= self.customer_data[i]['ready_time'],
                    f"early_time_{i}_{k}")
                model.addConstr(
                    arrival_time[i, k] <= self.customer_data[i]['due_date'],
                    f"late_time_{i}_{k}")
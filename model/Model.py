import gurobipy as gp
from gurobipy import GRB
import math
from model.Constraint import Constraint
from model.Objective import Objective

class Model:
    """
    CVRPTW模型类
    """
    def __init__(self, vehicle_data, customer_data):
        self.vehicle_data = vehicle_data  # 车辆数据
        self.customer_data = customer_data  # 客户数据
        self.n = len(customer_data)  # 客户数量
        self.num_vehicles = vehicle_data['number']  # 车辆数量
        self.model = gp.Model("VRP") # 创建模型
        self.x = None  # 决策变量
        self.load = None  # 负载变量

    def build_model(self):
        # 创建决策变量
        self.x = self.model.addVars(self.n, self.n, self.num_vehicles, vtype=GRB.BINARY, name="x")
        self.load = self.model.addVars(self.n, self.num_vehicles, vtype=GRB.CONTINUOUS, name="load")

        # 添加目标函数
        objective = Objective(self.customer_data, self.x, self.num_vehicles)
        self.model.setObjective(objective.build(), GRB.MINIMIZE)

        # 添加约束
        constraint = Constraint(self.customer_data, self.x, self.load, self.vehicle_data, self.num_vehicles)
        constraint.add_constraints(self.model)

    def optimize(self, time_limit = None):
        """
        优化模型并返回解决方案
        :param time_limit: 优化时间限制, 单位为秒, 默认为None(不设置时间限制)
        :return: 当前最优解
        """
        # 设置时间限制
        if time_limit is not None:
            self.model.setParam('TimeLimit', time_limit)

        # 开始
        self.model.optimize()

        # 检查状态
        if self.model.status == GRB.OPTIMAL:
            return self.extract_solution()
        elif self.model.status == GRB.TIME_LIMIT:
            # 如果达到时间限制但找到了可行解，也返回当前最佳解
            if self.model.SolCount > 0:
                return self.extract_solution()
        return None

    def extract_solution(self):
        routes = {}
        for k in range(self.num_vehicles):
            route = []
            for i in range(self.n):
                for j in range(self.n):
                    if self.x[i, j, k].x > 0.5:
                        route.append((i, j))
            routes[k] = route
        return routes

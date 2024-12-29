import math

class Objective:
    """
    目标函数类
    """
    def __init__(self, customer_data, x, num_vehicles):
        self.customer_data = customer_data # 客户数据
        self.x = x # 决策变量
        self.num_vehicles = num_vehicles # 车辆数量

    @staticmethod
    def distance(c1, c2):
        """
        计算两个客户之间的距离
        :param c1:
        :param c2:
        :return:
        """
        return math.sqrt((c1['x'] - c2['x']) ** 2 + (c1['y'] - c2['y']) ** 2)

    def build(self):
        """
        目标函数：最小化总距离
        :return:
        """
        obj = 0
        for i in range(len(self.customer_data)):
            for j in range(len(self.customer_data)):
                for k in range(self.num_vehicles):
                    obj += self.distance(self.customer_data[i], self.customer_data[j]) * self.x[i, j, k]
        return obj

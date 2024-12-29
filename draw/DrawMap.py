import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Rectangle
import random
import colorsys


class DrawMap:
    """
    绘制VRP问题的路线图
    """

    def __init__(self, customer_data, vehicle_data):
        self.customer_data = customer_data
        self.vehicle_data = vehicle_data
        self.num_vehicles = vehicle_data['number']
        self.colors = self.generate_colors(self.num_vehicles)

    @staticmethod
    def generate_colors(n):
        """
        生成n个视觉上分离度较高的颜色
        """
        colors = []
        for i in range(n):
            # 使用HSV颜色空间，均匀分布色调
            hue = i / n
            saturation = 0.7 + random.random() * 0.3  # 70%-100%的饱和度
            value = 0.7 + random.random() * 0.3  # 70%-100%的明度
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            colors.append(rgb)
        return colors

    def draw_customers(self, ax):
        """
        绘制客户点
        """
        # 绘制配送中心（depot）
        depot = self.customer_data[0]
        ax.scatter(depot['x'], depot['y'], c='red', s=200, marker='*', label='Depot')

        # 绘制客户点
        for customer in self.customer_data[1:]:  # 跳过depot
            x, y = customer['x'], customer['y']
            # 绘制客户点
            ax.scatter(x, y, c='blue', s=100)
            # 添加客户编号标签
            ax.annotate(f"C{customer['id']}", (x, y), xytext=(5, 5),
                        textcoords='offset points')

            # # 添加需求量标签
            # ax.annotate(f"D:{customer['demand']}", (x, y), xytext=(5, -10),
            #             textcoords='offset points', fontsize=8)

            # # 添加时间窗标签
            # time_window = f"[{customer['ready_time']},{customer['due_date']}]"
            # ax.annotate(time_window, (x, y), xytext=(5, -20),
            #             textcoords='offset points', fontsize=8)

    # def draw_routes(self, solution, ax):
    #     """
    #     绘制路线
    #     """
    #     for k, route in solution.items():
    #         color = self.colors[k]
    #         route_x = []
    #         route_y = []
    #
    #         # 绘制路线
    #         for i, j in route:
    #             # 起点坐标
    #             start_x = self.customer_data[i]['x']
    #             start_y = self.customer_data[i]['y']
    #             # 终点坐标
    #             end_x = self.customer_data[j]['x']
    #             end_y = self.customer_data[j]['y']
    #
    #             # 画箭头
    #             ax.arrow(start_x, start_y, end_x - start_x, end_y - start_y,
    #                      head_width=2, head_length=3, fc=color, ec=color,
    #                      length_includes_head=True, alpha=0.6)
    #
    #             route_x.extend([start_x, end_x])
    #             route_y.extend([start_y, end_y])
    #
    #         # 添加路线标签
    #         label = f'Vehicle {k + 1}'
    #         ax.plot(route_x, route_y, c=color, alpha=0.4, label=label)

    def draw_routes(self, solution, ax):
        """
        绘制路线
        """
        for k, route in solution.items():
            color = self.colors[k]

            # 绘制路线
            for i, j in route:
                # 起点坐标
                start_x = self.customer_data[i]['x']
                start_y = self.customer_data[i]['y']
                # 终点坐标
                end_x = self.customer_data[j]['x']
                end_y = self.customer_data[j]['y']

                # 画箭头
                ax.arrow(start_x, start_y, end_x - start_x, end_y - start_y,
                         head_width=2, head_length=3, fc=color, ec=color,
                         length_includes_head=True, alpha=0.6)

            # 添加路线标签 - 可以保留，但要确保label已定义
            label = f'Vehicle {k + 1}'

    def draw_solution(self, solution, title="VRP Solution"):
        """
        绘制完整的解决方案
        """
        fig, ax = plt.subplots(figsize=(12, 8))

        # 绘制客户点
        self.draw_customers(ax)

        # 绘制路线
        self.draw_routes(solution, ax)

        # 设置图表属性
        ax.set_title(title)
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()

        # 添加文本框显示车辆信息
        info_text = f"Number of Vehicles: {self.num_vehicles}\n"
        info_text += f"Vehicle Capacity: {self.vehicle_data['capacity']}"
        plt.text(0.02, 0.98, info_text, transform=ax.transAxes,
                 bbox=dict(facecolor='white', alpha=0.8),
                 verticalalignment='top')

        plt.tight_layout()
        return fig

    def save_figure(self, solution, filename, title="VRP Solution"):
        """
        保存绘图结果
        """
        fig = self.draw_solution(solution, title)
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close(fig)

    def show_figure(self, solution, title="VRP Solution"):
        """
        显示绘图结果
        """
        self.draw_solution(solution, title)
        plt.show()
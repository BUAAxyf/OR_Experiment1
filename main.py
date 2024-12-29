from read.Read import Read
from model.Model import Model
from draw.DrawMap import DrawMap

def solve_C101():
    # 读取数据
    vehicle_data, customer_data = Read.read_instance('D:\Project\OR_Experiment1\data\solomon_100\C101.txt')

    # 实例化
    model = Model(vehicle_data, customer_data)

    # 构建模型
    model.build_model()

    # 求解
    solution = model.optimize()

    # 输出
    if solution:
        print("Solution found:")
        for vehicle_id, route in solution.items():
            print(f"Vehicle {vehicle_id} route:")
            for i, j in route:
                print(f"  {i} -> {j}")

        # 创建绘图对象并显示结果
        draw_map = DrawMap(customer_data, vehicle_data)

        # 显示图形
        draw_map.show_figure(solution, "VRPTW Solution Visualization")

        # 保存图形
        draw_map.save_figure(solution, "result/vrp_solution.png")
    else:
        print("No optimal solution found")

def solve_all_instances():
    # 读取数据
    data = Read('data')
    for path in data.file_path_list():
        print(f"Solving instance: {path}")

        # 读取数据
        vehicle_data, customer_data = Read.read_instance(path)

        # 创建VRP模型
        model = Model(vehicle_data, customer_data)

        # 构建并求解模型
        model.build_model()
        solution = model.optimize(300) # 时间限制300s

        # 输出结果
        if solution:
            print("Solution found:")
            for vehicle_id, route in solution.items():
                print(f"Vehicle {vehicle_id} route:")
                for i, j in route:
                    print(f"  {i} -> {j}")

            # 创建绘图对象并显示结果
            draw_map = DrawMap(customer_data, vehicle_data)

            # 显示图形
            draw_map.show_figure(solution, "VRPTW Solution Visualization")

            # 保存图形（可选）
            draw_map.save_figure(solution, "result/vrp_solution.png")
        else:
            print(f"No optimal solution found for instance: {path}")

if __name__ == '__main__':
    solve_C101()
    # solve_all_instances()
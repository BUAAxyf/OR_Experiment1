import os

class Read:
    """
    读取算例文件并解析
    """
    def __init__(self, file_path):
        self.customer_data = {}
        self.vehicle_data = {}
        self.file_path = file_path
        self.file_paths = []
        self.file_names = []
        self.file_path_list()
        
    def file_path_list(self):
        """
        返回路径下的所有文件的路径的列表
        :return:
        """
        file_paths = []

        # 检查文件夹是否存在
        if not os.path.isdir(self.file_path):
            raise ValueError(f"路径 {self.file_path} 不是一个有效的目录。")

        # 遍历给定目录下的所有文件
        for root, dirs, files in os.walk(self.file_path):
            for file in files:
                # 获取文件的完整路径并添加到列表中
                full_path = os.path.join(root, file)
                file_paths.append(full_path)

        self.file_paths = file_paths

        return file_paths

    def read_instance_form_self(self, instance_path):
        # # 检查文件是否存在
        # if instance_path not in self.file_paths:
        #     raise ValueError(f"文件 {instance_path} 不存在于路径 {self.file_path} 中。")

        # 打开并读取文件内容
        with open(instance_path, 'r') as file:
            lines = file.readlines()

        # 分割并解析文件内容
        vehicle_data = {}
        customer_data = []

        # 解析文件头, 初始化车辆信息, 客户信息
        for i in range(0, 7):
            line = lines[i].strip()  # 去掉行首尾的空白字符

            # 文件名
            if i == 0:
                # file_name = line[0]
                continue

            # 车辆信息
            elif line.startswith('VEHICLE'):
                vehicle_number = int(lines[i + 2].split()[0])
                vehicle_capacity = int(lines[i + 2].split()[1])
                vehicle_data['number'] = vehicle_number
                vehicle_data['capacity'] = vehicle_capacity
            # 客户信息
            elif line.startswith('CUSTOMER'):
                break
            else:
                continue

            # 解析客户信息
            customer_data = []
            for line in lines[8:]:
                parts = line.strip().split()
                # 空行
                if not parts:
                    continue
                # 读取信息
                customer_info = {'id': int(parts[0]),
                                 'x': int(parts[1]),
                                 'y': int(parts[2]),
                                 'demand': int(parts[3]),
                                 'ready_time': int(parts[4]),
                                 'due_date': int(parts[5]) + int(parts[6]),
                                 'service_time': int(parts[6])}
                customer_data.append(customer_info)

        self.vehicle_data[instance_path] = vehicle_data
        self.customer_data[instance_path] = customer_data

        return vehicle_data, customer_data

    @staticmethod
    def read_instance(instance_path):
        """
        读取给定的算例名称文件并返回解析后的字典。
        :param instance_path: 算例文件的名称
        :return: 解析后的字典
        """
        # # 检查文件是否存在
        # if instance_path not in self.file_paths:
        #     raise ValueError(f"文件 {instance_path} 不存在于路径 {self.file_path} 中。")

        # 打开并读取文件内容
        with open(instance_path, 'r') as file:
            lines = file.readlines()

        # 分割并解析文件内容
        vehicle_data = {}
        customer_data = []

        # 解析文件头, 初始化车辆信息, 客户信息
        for i in range(0, 7):
            line = lines[i].strip()  # 去掉行首尾的空白字符

            # 文件名
            if i == 0:
                # file_name = line[0]
                continue

            # 车辆信息
            elif line.startswith('VEHICLE'):
                vehicle_number = int(lines[i+2].split()[0])
                vehicle_capacity = int(lines[i+2].split()[1])
                vehicle_data['number'] = vehicle_number
                vehicle_data['capacity'] = vehicle_capacity
            # 客户信息
            elif line.startswith('CUSTOMER'):
                break
            else:
                continue

            # 解析客户信息
            customer_data = []
            for line in lines[8:]:
                parts = line.strip().split()
                # 空行
                if not parts:
                    continue
                # 读取信息
                customer_info = {'id': int(parts[0]),
                                 'x': int(parts[1]),
                                 'y': int(parts[2]),
                                 'demand': int(parts[3]),
                                 'ready_time': int(parts[4]),
                                 'due_date': int(parts[5]) + int(parts[6]),
                                 'service_time': int(parts[6])}
                customer_data.append(customer_info)

        # self.vehicle_data[instance_path] = vehicle_data
        # self.customer_data[instance_path] = customer_data

        return vehicle_data, customer_data

if __name__ == '__main__':
    data = Read('..\\data')
    # print(data.file_paths)
    instance = data.file_paths[0]
    print(data.read_instance(instance))

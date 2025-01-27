import json
import pandas as pd
import winreg
from typing import Optional, Callable
import flet as ft


def Pretension_Loads_json_to_excel(data, excel_file_path):
    """
    将MIDAS Civil的预张力荷载JSON数据转换为Excel文件

    参数:
        data (dict): 从MIDAS API获取的预张力荷载JSON数据
        excel_file_path (str): 要保存的Excel文件路径

    返回:
        None

    处理过程:
        1. 解析JSON数据结构，提取每个单元的预张力信息
        2. 将数据整理为表格形式
        3. 使用Pandas创建DataFrame
        4. 将DataFrame保存为Excel文件
    """

    rows = []
    for key, value in data["PTNS"].items():
        item = value["ITEMS"][0]
        row = {
            "单元号": key,
            "ID": item["ID"],
            "荷载工况名称": item["LCNAME"],
            "组名称": item["GROUP_NAME"],
            "张力": item["TENSION"],
        }
        rows.append(row)

    # 创建 DataFrame
    df = pd.DataFrame(rows)

    # 保存为 Excel 文件
    df.to_excel(excel_file_path, index=False)


def Pretension_Loads_json_to_df(data):
    """
    将MIDAS Civil的预张力荷载JSON数据转换为Pandas DataFrame

    参数:
        data (dict): 从MIDAS API获取的预张力荷载JSON数据

    返回:
        pd.DataFrame: 包含预张力信息的DataFrame

    处理过程:
        1. 解析JSON数据结构，提取每个单元的预张力信息
        2. 将数据整理为表格形式
        3. 使用Pandas创建并返回DataFrame
    """

    rows = []
    for key, value in data["Assign"].items():
        item = value["ITEMS"][0]
        row = {
            "单元号": key,
            "ID": item["ID"],
            "荷载工况名称": item["LCNAME"],
            "组名称": item["GROUP_NAME"],
            "张力": item["TENSION"],
        }
        rows.append(row)

    # 创建 DataFrame
    df = pd.DataFrame(rows)
    return df


def Pretension_Loads_df_to_json(df):
    """
    将包含预张力信息的Pandas DataFrame转换为MIDAS Civil所需的JSON格式

    参数:
        df (pd.DataFrame): 包含预张力信息的DataFrame，必须包含以下列：
            - 单元号: 单元编号
            - ID: 荷载ID
            - 荷载工况名称: 荷载工况名称
            - 组名称: 荷载组名称
            - 张力: 预张力值

    返回:
        dict: 符合MIDAS Civil API要求的JSON数据结构

    处理过程:
        1. 将DataFrame转换为字典列表
        2. 按照MIDAS Civil API要求的格式重新构建JSON结构
        3. 返回最终的JSON数据
    """
    # 将 DataFrame 转换为字典列表
    data_list = df.to_dict(orient="records")
    # 重新构建 JSON 数据结构
    ptns_dict = {}
    for item in data_list:
        key = item["单元号"]
        sub_dict = {
            "ITEMS": [
                {
                    "ID": item["ID"],
                    "LCNAME": item["荷载工况名称"],
                    "GROUP_NAME": item["组名称"],
                    "TENSION": item["张力"],
                }
            ]
        }
        ptns_dict[key] = sub_dict

    final_json = {"Assign": ptns_dict}
    return final_json


def truss_force_tablejson_to_table(json_data):
    data = json_data["TrussForce"]
    headers = data["HEAD"]
    df = pd.DataFrame(data["DATA"], columns=headers)
    return df


def Pretension_Loads_excel_to_json(excel_file_path, json_file_path):
    """
    将包含预张力信息的Excel文件转换为MIDAS Civil所需的JSON格式，并保存为JSON文件。

    参数:
        excel_file_path (str): 包含预张力信息的Excel文件路径。Excel文件必须包含以下列：
            - 单元号: 单元编号
            - ID: 荷载ID
            - 荷载工况名称: 荷载工况名称
            - 组名称: 荷载组名称
            - 张力: 预张力值
        json_file_path (str): 要保存的JSON文件路径。

    返回:
        None

    处理过程:
        1. 从Excel文件中读取数据并转换为Pandas DataFrame。
        2. 将DataFrame转换为字典列表。
        3. 按照MIDAS Civil API要求的格式重新构建JSON结构。
        4. 将最终的JSON数据写入指定的JSON文件。
    """
    # 读取 Excel 文件
    df = pd.read_excel(excel_file_path)

    # 将 DataFrame 转换为字典列表
    data_list = df.to_dict(orient="records")

    # 重新构建 JSON 数据结构
    ptns_dict = {}
    for item in data_list:
        key = item["单元号"]
        sub_dict = {
            "ITEMS": [
                {
                    "ID": item["ID"],
                    "LCNAME": item["荷载工况名称"],
                    "GROUP_NAME": item["组名称"],
                    "TENSION": item["张力"],
                }
            ]
        }
        ptns_dict[key] = sub_dict

    final_json = {"Assign": ptns_dict}

    # 将数据写入 JSON 文件
    with open(json_file_path, "w", encoding="utf - 8") as f:
        json.dump(final_json, f, ensure_ascii=False, indent=4)


class MidasConfig:
    def __init__(self):
        self.base_url, self.api_key = self._get_midas_connection()

    def _get_midas_connection(self):
        """从注册表获取MIDAS连接信息"""
        reg_path = r"SOFTWARE\MIDAS\CVLwNX_CH\CONNECTION"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            uri = winreg.QueryValueEx(key, "URI")[0]
            port = winreg.QueryValueEx(key, "PORT")[0]
            api_key = winreg.QueryValueEx(key, "Key")[0]

            # 设置STARTUP
            try:
                winreg.SetValueEx(key, "STARTUP", 0, winreg.REG_DWORD, 1)
            except WindowsError:
                pass

        base_url = f"https://{uri}:{port}/civil"
        return base_url, api_key


# 定义一个名为 EditableDataFrame 的类，继承自 ft.Card
class EditableDataFrame(ft.Card):
    def __init__(
        self,
        df: pd.DataFrame,  # 传入一个 Pandas DataFrame 对象，用于初始化表格数据
        on_change: Optional[
            Callable[[pd.DataFrame], None]
        ] = None,  # 可选的回调函数，当表格数据改变时调用
        max_height: int = 400,  # 表格的最大高度，默认为 400 像素
    ):
        super().__init__()  # 调用父类的构造函数
        self.df = df.copy()  # 深拷贝传入的 DataFrame，避免对原始数据的修改
        self.on_change = on_change  # 保存传入的回调函数
        self.max_height = max_height  # 保存传入的最大高度
        self.edited_cells = {}  # 用于存储已编辑的单元格
        self.data_table = ft.DataTable(
            columns=self._create_columns(),  # 调用 _create_columns 方法创建表格列
            rows=self._create_rows(),  # 调用 _create_rows 方法创建表格行
            horizontal_lines=ft.border.BorderSide(
                1, ft.colors.OUTLINE_VARIANT
            ),  # 设置水平分割线样式
            heading_row_height=50,  # 设置表头行的高度
            data_row_max_height=45,  # 设置数据行的最大高度
        )
        self.md1 = """
# 使用帮助
- 使用前需建立包含完整施工过程
- 输入误差阈值(%)
- 点击“获取初始信息”按钮可获取当前模型的初拉力信息,并保存在init_tension.xlsx文件中
- 通过编辑UI界面中的表格或本地的init_tension.xlsx文件输入目标成桥索力(软件直接采用目标成桥索力作为迭代初始值)
- 点击“开始计算”按钮,并在弹出的对话框中选择目标索力数据源,开始迭代计算,直到偏差百分比均小于给的阈值,或达到最大迭代次数20次
"""

        self.tips = ft.Markdown(
            self.md1,
            selectable=True,
            expand=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
        )
        # 包装在滚动容器中
        self.content = ft.Row(
            [
                self.tips,  # 将 Markdown 控件添加到 Row 控件中
                ft.Column(
                    controls=[self.data_table],  # 将表格添加到 Column 控件中
                    scroll=ft.ScrollMode.ALWAYS,  # 设置 Column 控件的滚动模式为始终滚动
                    height=300,  # 设置 Column 控件的高度
                ),
            ]
        )
        self.color = ft.colors.SURFACE

    def _create_columns(self):
        """
        创建并返回表格的列定义
        """
        columns = []  # 初始化一个空列表，用于存储列定义
        for col in self.df.columns:  # 遍历 DataFrame 的列名
            columns.append(
                ft.DataColumn(
                    ft.Text(
                        str(col), weight=ft.FontWeight.BOLD, width=85
                    ),  # 创建一个 DataColumn，包含一个 Text 控件，显示列名，并设置字体加粗和宽度
                    numeric=pd.api.types.is_numeric_dtype(
                        self.df[col]
                    ),  # 根据列的数据类型设置 numeric 属性
                )
            )
        return columns  # 返回列定义列表

    def _create_rows(self):
        """
        创建并返回表格的行定义
        """
        rows = []  # 初始化一个空列表，用于存储行定义
        for row_idx, row in self.df.iterrows():  # 遍历 DataFrame 的行
            cells = []  # 初始化一个空列表，用于存储单元格定义
            for col_idx, value in enumerate(row):  # 遍历行中的每个值
                cell = ft.DataCell(
                    ft.TextField(
                        value=str(value),  # 创建一个 TextField 控件，显示单元格的值
                        border="none",  # 设置边框为无
                        height=50,  # 设置高度
                        read_only=True,  # 设置为只读
                        on_focus=lambda e,
                        r=row_idx,
                        c=col_idx: self._handle_cell_focus(
                            e, r, c
                        ),  # 设置获得焦点时的回调函数
                        on_blur=lambda e, r=row_idx, c=col_idx: self._handle_cell_blur(
                            e, r, c
                        ),  # 设置失去焦点时的回调函数
                        expand=True,
                    )
                )
                cells.append(cell)  # 将单元格添加到 cells 列表中
            rows.append(
                ft.DataRow(cells=cells)
            )  # 将 cells 列表添加到 rows 列表中，创建一个 DataRow
        return rows  # 返回行定义列表

    def _handle_cell_focus(self, e, row_idx, col_idx):
        """
        处理单元格获得焦点的事件
        """
        # 双击启用编辑
        tf = e.control  # 获取触发事件的 TextField 控件
        tf.read_only = False  # 设置为可编辑
        tf.border = ft.InputBorder.OUTLINE  # 设置边框样式为外边框
        tf.update()  # 更新控件状态

    def _handle_cell_blur(self, e, row_idx, col_idx):
        """
        处理单元格失去焦点的事件
        """
        tf = e.control  # 获取触发事件的 TextField 控件
        new_value = tf.value  # 获取编辑后的新值
        col_name = self.df.columns[col_idx]  # 获取列名

        # 尝试转换数据类型
        try:
            if pd.api.types.is_numeric_dtype(self.df[col_name]):  # 如果列是数值类型
                new_value = (
                    float(new_value) if "." in new_value else int(new_value)
                )  # 将新值转换为浮点数或整数
        except ValueError:  # 如果转换失败
            # 如果转换失败，恢复原值
            new_value = self.df.iloc[row_idx, col_idx]  # 恢复为原始值
            tf.value = str(new_value)  # 设置 TextField 的值为原始值

        # 更新 DataFrame
        self.df.iloc[row_idx, col_idx] = new_value  # 更新 DataFrame 中的值

        # 重置单元格样式
        tf.read_only = True  # 设置为只读
        tf.border = "none"  # 设置边框为无
        tf.update()  # 更新控件状态

        # 触发回调
        if self.on_change:  # 如果存在回调函数
            self.on_change(self.df)  # 调用回调函数，传入更新后的 DataFrame

    def update_data(self, new_df: pd.DataFrame):
        """
        更新显示的数据
        """
        self.df = new_df.copy()  # 深拷贝传入的 DataFrame，避免对原始数据的修改
        self.data_table.rows = self._create_rows()  # 重新创建表格行
        self.update()  # 更新控件状态


if __name__ == "__main__":
    json_file_path = "./target.json"
    excel_file_path = "result.xlsx"
    # json_to_excel(json_file_path, excel_file_path)
    Pretension_Loads_excel_to_json(excel_file_path, json_file_path)
    # value = data['PTNS'].get("2001")
    # item = value['ITEMS'][0]
    #

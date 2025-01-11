import flet as ft
import pandas as pd
import json
from api import MidasAPI, compute_tension
from tools import (
    Pretension_Loads_df_to_json,
    Pretension_Loads_json_to_df,
    Pretension_Loads_json_to_excel,
)
from typing import Optional, Callable


# 定义一个名为 EditableDataFrame 的类，继承自 ft.UserControl
class EditableDataFrame(ft.UserControl):
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

    def build(self):
        """
        构建并返回用户界面的控件树
        """
        # 创建表格
        self.data_table = ft.DataTable(
            columns=self._create_columns(),  # 调用 _create_columns 方法创建表格列
            rows=self._create_rows(),  # 调用 _create_rows 方法创建表格行
            vertical_lines=ft.border.BorderSide(1, "#E0E0E0"),  # 设置垂直分割线样式
            horizontal_lines=ft.border.BorderSide(1, "#E0E0E0"),  # 设置水平分割线样式
            heading_row_color="#F5F5F5",  # 设置表头行的背景颜色
            heading_row_height=50,  # 设置表头行的高度
            data_row_max_height=45,  # 设置数据行的最大高度
            width=900,  # 设置表格的宽度
        )

        # 包装在滚动容器中
        return ft.Container(
            content=ft.Column(
                controls=[self.data_table],  # 将表格添加到 Column 控件中
                scroll=ft.ScrollMode.ALWAYS,  # 设置 Column 控件的滚动模式为始终滚动
                height=300,  # 设置 Column 控件的高度
            )
        )

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
                        width=150,  # 设置宽度
                        # text_size=14,  # 设置字体大小
                        # content_padding=5,  # 设置内容内边距
                        read_only=True,  # 设置为只读
                        on_focus=lambda e, r=row_idx, c=col_idx: self._handle_cell_focus(
                            e, r, c
                        ),  # 设置获得焦点时的回调函数
                        on_blur=lambda e, r=row_idx, c=col_idx: self._handle_cell_blur(
                            e, r, c
                        ),  # 设置失去焦点时的回调函数
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


def main(page: ft.Page):
    df = pd.DataFrame(
        {"单元号": [0], "ID": [0], "荷载工况名称": [0], "组名称": [0], "张力": [0]}
    )

    def handle_close_xlsx(e):
        """
        处理关闭选择xlsx文件的对话框事件
        """
        global df  # 声明df为全局变量
        page.close(dlg_modal)  # 关闭对话框
        df = pd.read_excel("init_tension.xlsx")  # 从xlsx文件中读取数据并更新df
        # 将DataFrame转换为JSON并保存为target.json和tension.json
        target_json = Pretension_Loads_df_to_json(df)  # 将DataFrame转换为JSON格式
        with open("target.json", "w") as f:  # 打开target.json文件
            json.dump(target_json, f)  # 将JSON数据写入文件
        with open("tension.json", "w") as f:  # 打开tension.json文件
            json.dump(target_json, f)  # 将JSON数据写入文件

        # 调用compute_tension函数进行迭代计算
        df = compute_tension("tension.json", "target.json")  # 调用compute_tension函数进行迭代计算

        df = pd.DataFrame(
            {
                "单元号": df["单元号"],
                "目标索力": df["张力"],
                "实际索力": df["正装成桥索力"],
                "偏差": df["偏差"],
                "偏差百分比": df["偏差百分比"],
            }
        )

        # 显示成功信息
        message_text.value = "索力计算完成！"  # 更新提示信息
        data_frame.update_data(df)  # 更新数据框
        page.update()  # 更新页面


    def handle_close_ui(e):
        """
        处理关闭选择UI表格的对话框事件
        """
        global df
        page.close(dlg_modal)
        # 获取当前显示的数据
        df = data_frame.df
        # 将DataFrame转换为JSON并保存为target.json和tension.json
        target_json = Pretension_Loads_df_to_json(df)
        with open("target.json", "w") as f:
            json.dump(target_json, f)
        with open("tension.json", "w") as f:
            json.dump(target_json, f)

        # 调用compute_tension函数进行迭代计算
        df = compute_tension("tension.json", "target.json")
        df = pd.DataFrame(
            {
                "单元号": df["单元号"],
                "目标索力": df["张力"],
                "实际索力": df["正装成桥索力"],
                "偏差": df["偏差"],
                "偏差百分比": df["偏差百分比"],
            }
        )

        # 显示成功信息
        message_text.value = "索力计算完成！"
        data_frame.update_data(df)
        page.update()


    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.fonts = {
        "MiSans": "fonts/MiSans-Regular.ttf",
    }
    page.theme = ft.Theme(font_family="MiSans")
    title = ft.Text("索力计算", size=28, weight=ft.FontWeight.BOLD, color="#1565C0")

    # 创建一个文本框用于显示提示信息
    message_text = ft.Text(size=14, color="#4CAF50", weight=ft.FontWeight.W_500)

    # 创建一个按钮用于获取索力数据
    get_data_button = ft.ElevatedButton(
        content=ft.Row(
            [
                ft.Icon(name=ft.Icons.GET_APP, color="white"),
                ft.Text("获取初始信息", color="white", size=16),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        style=ft.ButtonStyle(
            color="white",
            bgcolor="#1976D2",
            padding=20,
            animation_duration=300,
        ),
        on_click=lambda _: get_data(),
    )

    error_tolerance_input = ft.TextField(
        label="误差允许值（百分比）", value="0.15", width=200
    )

    # 创建一个按钮用于开始计算
    start_calculation_button = ft.ElevatedButton(
        content=ft.Row(
            [
                ft.Icon(name=ft.icons.CALCULATE, color="white"),
                ft.Text("开始计算", color="white", size=16),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        style=ft.ButtonStyle(
            color="white",
            bgcolor="#1976D2",
            padding=20,
            animation_duration=300,
        ),
        on_click=lambda _: start_calculation(),
    )

    # 创建一个可编辑的数据框
    data_frame = EditableDataFrame(df)

    dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("请选择"),
        content=ft.Text("初始施工索力来源于init_tension.xlsx或table in UI"),
        actions=[
            ft.TextButton("xlsx", on_click=handle_close_xlsx),
            ft.TextButton("table in UI", on_click=handle_close_ui),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # 将组件添加到页面
    page.add(
        ft.Container(content=title, margin=ft.margin.only(bottom=20)),
        ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [message_text, error_tolerance_input],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        margin=ft.margin.only(bottom=30),
                        width=900,
                    ),
                    ft.Container(
                        content=data_frame,
                        margin=ft.margin.only(bottom=30),
                        padding=20,
                        bgcolor="white",
                        border_radius=10,
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=10,
                            color=ft.colors.BLACK12,
                        ),
                    ),
                    ft.Row(
                        [get_data_button, start_calculation_button],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=5,
        ),
    )

    def get_data():
        """
        获取索力数据并更新数据框
        """
        try:
            # 调用MidasAPI获取索力数据
            data = MidasAPI("GET", "/db/PTNS")
            # 将获取的数据保存为Excel文件
            Pretension_Loads_json_to_excel(data, "init_tension.xlsx")

            # 从Excel文件中读取数据并更新数据框
            df = pd.read_excel("init_tension.xlsx")

            # 更新数据框
            data_frame.update_data(df)

            # 显示成功信息
            message_text.value = "索力数据获取成功！"
            page.update()

        except Exception as e:
            # 显示错误信息
            message_text.value = f"获取索力数据时发生错误：{str(e)}"
            page.update()


    def start_calculation():
        """
        开始索力计算的函数
        """
        try:
            # 弹出对话框，选择本地的init_tension.xlsx文件或者UI界面的表格作为数据源
            page.open(dlg_modal)

        except Exception as e:
            # 显示错误信息
            message_text.value = f"索力计算时发生错误：{str(e)}"
            page.update()


ft.app(target=main)

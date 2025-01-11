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


class EditableDataFrame(ft.UserControl):
    def __init__(
        self,
        df: pd.DataFrame,
        on_change: Optional[Callable[[pd.DataFrame], None]] = None,
        max_height: int = 400,
    ):
        super().__init__()
        self.df = df.copy()
        self.on_change = on_change
        self.max_height = max_height
        self.edited_cells = {}

    def build(self):
        # 创建表格
        self.data_table = ft.DataTable(
            columns=self._create_columns(),
            rows=self._create_rows(),
            vertical_lines=ft.border.BorderSide(1, "#E0E0E0"),
            horizontal_lines=ft.border.BorderSide(1, "#E0E0E0"),
            heading_row_color="#F5F5F5",
            heading_row_height=50,
            data_row_max_height=45,
            width=900,
        )

        # 包装在滚动容器中
        return ft.Container(
            content=ft.Column(
                controls=[self.data_table],
                scroll=ft.ScrollMode.ALWAYS,
                height=300,
            )
        )

    def _create_columns(self):
        columns = []
        for col in self.df.columns:
            columns.append(
                ft.DataColumn(
                    ft.Text(str(col), weight=ft.FontWeight.BOLD, width=85),
                    numeric=pd.api.types.is_numeric_dtype(self.df[col]),
                )
            )
        return columns

    def _create_rows(self):
        rows = []
        for row_idx, row in self.df.iterrows():
            cells = []
            for col_idx, value in enumerate(row):
                cell = ft.DataCell(
                    ft.TextField(
                        value=str(value),
                        border="none",
                        height=50,
                        width=150,
                        # text_size=14,
                        # content_padding=5,
                        read_only=True,
                        on_focus=lambda e, r=row_idx, c=col_idx: self._handle_cell_focus(
                            e, r, c
                        ),
                        on_blur=lambda e, r=row_idx, c=col_idx: self._handle_cell_blur(
                            e, r, c
                        ),
                    )
                )
                cells.append(cell)
            rows.append(ft.DataRow(cells=cells))
        return rows

    def _handle_cell_focus(self, e, row_idx, col_idx):
        # 双击启用编辑
        tf = e.control
        tf.read_only = False
        tf.border = ft.InputBorder.OUTLINE
        tf.update()

    def _handle_cell_blur(self, e, row_idx, col_idx):
        tf = e.control
        new_value = tf.value
        col_name = self.df.columns[col_idx]

        # 尝试转换数据类型
        try:
            if pd.api.types.is_numeric_dtype(self.df[col_name]):
                new_value = float(new_value) if "." in new_value else int(new_value)
        except ValueError:
            # 如果转换失败，恢复原值
            new_value = self.df.iloc[row_idx, col_idx]
            tf.value = str(new_value)

        # 更新DataFrame
        self.df.iloc[row_idx, col_idx] = new_value

        # 重置单元格样式
        tf.read_only = True
        tf.border = "none"
        tf.update()

        # 触发回调
        if self.on_change:
            self.on_change(self.df)

    def update_data(self, new_df: pd.DataFrame):
        """更新显示的数据"""
        self.df = new_df.copy()
        self.data_table.rows = self._create_rows()
        self.update()


def main(page: ft.Page):
    df = pd.DataFrame(
        {"单元号": [0], "ID": [0], "荷载工况名称": [0], "组名称": [0], "张力": [0]}
    )

    def handle_close_xlsx(e):
        global df
        page.close(dlg_modal)
        df = pd.read_excel("init_tension.xlsx")
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

    def handle_close_ui(e):
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
                ft.Icon(name=ft.icons.CALCULATE, color="white"),
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
                        content=message_text, margin=ft.margin.only(bottom=30)
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
        try:
            # 调用MidasAPI获取索力数据
            data = MidasAPI("GET", "/db/PTNS")
            Pretension_Loads_json_to_excel(data, "init_tension.xlsx")

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
        try:
            # 弹出对话框，选择本地的init_tension.xlsx文件或者UI界面的表格作为数据源
            page.open(dlg_modal)

        except Exception as e:
            # 显示错误信息
            message_text.value = f"索力计算时发生错误：{str(e)}"
            page.update()


ft.app(target=main)

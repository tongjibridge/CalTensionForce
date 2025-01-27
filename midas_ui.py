import flet as ft
import pandas as pd
import json
from api import MidasAPI, compute_tension
from tools import *
from flet.core.constrained_control import ConstrainedControl


def main(page: ft.Page):
    df = pd.DataFrame(
        {
            "单元号": ["0"],
            "ID": ["0"],
            "荷载工况名称": ["0"],
            "组名称": ["0"],
            "张力": [0],
        }
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
        df = compute_tension(
            "tension.json", "target.json", float(error_tolerance_input.value)
        )  # 调用compute_tension函数进行迭代计算

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
        df = compute_tension(
            "tension.json", "target.json", float(error_tolerance_input.value)
        )
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
    page.theme = ft.Theme(
        font_family="MiSans", color_scheme_seed=ft.colors.BLUE, use_material3=True
    )
    page.window_width = 1200
    page.window_height = 600
    page.window_center()

    title = ft.AppBar(
        leading=ft.Icon(
            name=ft.icons.CALCULATE_OUTLINED,
            size=24,
            color=ft.colors.ON_PRIMARY,
        ),
        leading_width=40,
        center_title=False,
        title=ft.Text(
            "索力计算", size=20, weight=ft.FontWeight.W_500, color=ft.colors.ON_PRIMARY
        ),
        bgcolor=ft.colors.PRIMARY,
    )

    # 创建一个文本框用于显示提示信息
    message_text = ft.Text(
        size=14, color=ft.colors.GREEN_700, weight=ft.FontWeight.W_500
    )

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
            bgcolor=ft.colors.PRIMARY,
            padding=20,
            animation_duration=300,
        ),
        on_click=lambda _: get_data(),
    )

    # 创建一个文本框用于输入误差允许值（百分比）
    error_tolerance_input = ft.TextField(
        # 设置文本框的标签为“误差允许值（百分比）”
        label="误差允许值（百分比）",
        # 设置文本框的初始值为“0.15”
        value="0.15",
        # 设置文本框的宽度为200像素
        width=200,
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
            bgcolor=ft.colors.PRIMARY,
            padding=20,
            animation_duration=300,
        ),
        on_click=lambda _: start_calculation(),
    )

    status_card = ft.Card(
        content=ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            ft.Icon(
                                name=ft.icons.INFO,
                                color=ft.colors.GREEN_400,
                                size=20,
                            ),
                            message_text,
                        ]
                    ),
                    error_tolerance_input,
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=15,
        ),
        elevation=1,
    )

    # 创建一个可编辑的数据表
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
        title,
        ft.Container(
            content=ft.Column(
                [
                    status_card,
                    data_frame,
                    ft.Row(
                        [get_data_button, start_calculation_button],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                spacing=16,
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=0,
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

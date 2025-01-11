import flet as ft
import pandas as pd
import json
from api import MidasAPI, compute_tension
from tools import Pretension_Loads_df_to_json, truss_force_tablejson_to_table


def main(page: ft.Page):
    page.title = "索力计算"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # 创建一个文本框用于显示提示信息
    message_text = ft.Text()

    # 创建一个按钮用于获取索力数据
    get_data_button = ft.ElevatedButton("获取索力", on_click=lambda _: get_data())

    # 创建一个表格用于显示索力数据
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("单元号")),
            ft.DataColumn(ft.Text("索力")),
        ],
        rows=[],
    )

    # 创建一个按钮用于开始计算
    start_calculation_button = ft.ElevatedButton(
        "开始计算", on_click=lambda _: start_calculation()
    )

    # 将组件添加到页面
    page.add(
        message_text,
        get_data_button,
        data_table,
        start_calculation_button,
    )

    def get_data():
        try:
            # 调用MidasAPI获取索力数据
            data = MidasAPI("GET", "/db/PTNS")

            # 将JSON数据转换为DataFrame
            df = pd.DataFrame(data["PTNS"]).T

            # 清空表格数据
            data_table.rows.clear()

            # 将DataFrame数据添加到表格中
            for index, row in df.iterrows():
                data_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(index)),
                            ft.DataCell(ft.Text(row["ITEMS"][0]["TENSION"])),
                        ]
                    )
                )

            # 更新页面
            page.update()

            # 显示成功信息
            message_text.value = "索力数据获取成功！"
            page.update()

        except Exception as e:
            # 显示错误信息
            message_text.value = f"获取索力数据时发生错误：{str(e)}"
            page.update()

    def start_calculation():
        try:
            # 将表格数据转换为DataFrame
            df = pd.DataFrame(
                [
                    {
                        "单元号": row.cells[0].content.value,
                        "索力": row.cells[1].content.value,
                    }
                    for row in data_table.rows
                ]
            )

            # 将DataFrame转换为JSON并保存为target.json和tension.json
            target_json = Pretension_Loads_df_to_json(df)
            with open("target.json", "w") as f:
                json.dump(target_json, f)
            with open("tension.json", "w") as f:
                json.dump(target_json, f)

            # 调用compute_tension函数进行迭代计算
            compute_tension("tension.json", "target.json")

            # 显示成功信息
            message_text.value = "索力计算完成！"
            page.update()

        except Exception as e:
            # 显示错误信息
            message_text.value = f"索力计算时发生错误：{str(e)}"
            page.update()


ft.app(target=main)

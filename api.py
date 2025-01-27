# ruff: noqa: F401
import requests
import json
from tools import (
    MidasConfig,
    Pretension_Loads_df_to_json,
    truss_force_tablejson_to_table,
    Pretension_Loads_json_to_df,
)
import os
import re

# 创建MidasConfig实例
midas_config = MidasConfig()

# 使用配置信息
base_url = midas_config.base_url
api_key = midas_config.api_key


# 定义一个名为 MidasAPI 的函数，用于与 Midas Civil API 进行交互
def MidasAPI(method, command, body=None):
    # 使用从MidasConfig获取的base_url和api_key
    headers = {"Content-Type": "application/json", "MAPI-Key": api_key}
    url = base_url + command

    # 使用requests库发送HTTP请求
    response = requests.request(method=method, url=url, headers=headers, json=body)

    # 打印请求的方法、命令和响应的状态码
    print(method, command, response.status_code)

    # 返回响应的JSON数据
    return response.json()


def delete_iteration_files():
    """
    删除当前目录下所有以"迭代"开头并以".xlsx"结尾的文件。

    这个函数遍历当前目录中的所有文件，检查每个文件名是否以"迭代"开头并以".xlsx"结尾。
    如果是，则删除该文件，并打印一条消息表示文件已被删除。
    """
    for filename in os.listdir("."):
        # 检查文件名是否以"迭代"开头并以".xlsx"结尾
        if filename.startswith("迭代") and filename.endswith(".xlsx"):
            # 删除文件
            os.remove(filename)
            # 打印一条消息表示文件已被删除
            print(f"Deleted file: {filename}")


def compute_tension(tension: str, target: str, eps: float = 0.15):
    """
    计算并调整索力，直到偏差百分比满足要求。

    :param tension: 包含索力数据的JSON文件路径。
    :param target: 目标索力数据的JSON文件路径。
    :param eps: 允许的最大偏差百分比，默认为0.15。
    """
    # 删除运行目录里名称为迭代+数字的xlsx文件
    delete_iteration_files()

    # 读取目标JSON文件
    with open(target, "r", encoding="utf-8") as f:
        target_json = json.load(f)
    # 将目标JSON文件转换为DataFrame
    target_tension = Pretension_Loads_json_to_df(target_json)
    # 将单元号转换为整数并转换为列表
    eles = target_tension["单元号"].astype(int)
    eles = eles.tolist()

    # 获取当前文件夹的路径
    current_folder = os.getcwd()

    # 获取所有阶段的信息
    allstage = MidasAPI("GET", "/db/STAG", {})
    # 获取最后一个阶段的信息
    last_step_information = list(allstage["STAG"].items())[-1]
    # 获取最后一个阶段的名称
    stagename = last_step_information[-1]["NAME"]

    # 读取索力JSON文件
    with open(tension, "r", encoding="utf-8") as f:
        tension_json = json.load(f)

    # 初始化迭代次数
    n = 0

    # 开始迭代，直到偏差百分比满足要求或达到最大迭代次数
    while True:
        n += 1
        # 如果迭代次数超过20次，跳出循环
        if n > 20:
            break
        # 发送PUT请求更新索力数据
        MidasAPI("PUT", "/db/PTNS", tension_json)
        # 发送POST请求进行分析
        MidasAPI("POST", "/doc/Anal", {})
        if n == 1:
            # 获取最后的step
            POST_json = {
                "Argument": {
                    "TABLE_NAME": "TrussForce",
                    "TABLE_TYPE": "TRUSSFORCE",
                    "EXPORT_PATH": "E:\\CAE\\model\\mgfl\\api\\Output2.json",
                    "UNIT": {"FORCE": "kN", "DIST": "m"},
                    "STYLES": {"FORMAT": "Fixed", "PLACE": 12},
                    "COMPONENTS": [
                        "Elem",
                        "Load",
                        "Stage",
                        "Step",
                        "Force-I",
                        "Force-J",
                    ],
                    "NODE_ELEMS": {"KEYS": [eles[0]]},
                    "LOAD_CASE_NAMES": ["合计(CS)"],
                    "OPT_CS": True,
                }
            }
            MidasAPI("POST", "/POST/TABLE", POST_json)
            with open(
                "Output2.json",
                "r",
                encoding="gbk",
                errors="ignore",
            ) as f:
                temp_json2 = f.read()
            extracted_string = re.search(r"(\"TrussForce\":+)(.+)}", temp_json2).group(
                0
            )
            temp_json2 = json.loads("{" + extracted_string)
            temp_value2 = truss_force_tablejson_to_table(temp_json2)
            step_name = temp_value2["Step"].iloc[-3]

            # 格式化阶段步骤名称
            STAGE_STEP = f"{stagename}:{step_name}"

            # 定义POST请求的JSON数据
            POST_json = {
                "Argument": {
                    "TABLE_NAME": "TrussForce",
                    "TABLE_TYPE": "TRUSSFORCE",
                    "EXPORT_PATH": f"{current_folder}\\Output.json",
                    "UNIT": {"FORCE": "N", "DIST": "m"},
                    "STYLES": {"FORMAT": "Fixed", "PLACE": 12},
                    "COMPONENTS": [
                        "Elem",
                        "Load",
                        "Stage",
                        "Step",
                        "Force-I",
                        "Force-J",
                    ],
                    "NODE_ELEMS": {"KEYS": eles},
                    "LOAD_CASE_NAMES": ["合计(CS)"],
                    "OPT_CS": True,
                    "STAGE_STEP": [STAGE_STEP],
                }
            }

        # 发送POST请求导出表格数据
        MidasAPI("POST", "/POST/TABLE", POST_json)

        # 读取导出的JSON文件
        with open(
            f"{current_folder}\\Output.json",
            "r",
            encoding="utf-8-sig",
            errors="replace",
        ) as f:
            temp_json = json.load(f)

        # 将导出的JSON文件转换为表格数据
        temp_value = truss_force_tablejson_to_table(temp_json)

        # 将索力JSON文件转换为DataFrame
        tension_value = Pretension_Loads_json_to_df(tension_json)

        # 更新目标索力DataFrame中的施工索力、正装成桥索力、偏差和偏差百分比列
        target_tension["施工索力"] = tension_value["张力"].astype(float)
        target_tension["正装成桥索力"] = temp_value["Force-I"].astype(float)
        target_tension["偏差"] = target_tension["正装成桥索力"].astype(
            float
        ) - target_tension["张力"].astype(float)
        target_tension["偏差百分比"] = (
            100.0
            * target_tension["偏差"].astype(float)
            / target_tension["张力"].astype(float)
        )

        # 将目标索力DataFrame保存为Excel文件
        target_tension.to_excel(f"迭代{n:02d}.xlsx", index=False)

        # 如果偏差百分比的绝对值均小于0.15%，结束循环
        if abs(target_tension["偏差百分比"]).max() < eps:
            break

        # 更新索力JSON文件中的张力数据
        tension_value["张力"] = tension_value["张力"] - target_tension["偏差"]
        tension_json = Pretension_Loads_df_to_json(tension_value)
    return target_tension


if __name__ == "__main__":
    # compute_tension("target.json", "tension.json")
    # 测试代码1——获取初拉力
    # # ljson = MidasAPI("GET", "/db/PTNS")

    # # # save json
    # # with open("accounts3.json", "w") as f:
    # #     f.write(json.dumps(ljson))

    # # elementIDS=["2001","2002","2003","2004","2005","2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019","2020","2021","2022","2023","2024","2025","2026","2027","2028","2029","2030","2031","2032","2033","2034","2035","2036","2037","2038","2039","2040","2041","2042","2043","2044","2045","2046","2047","2048","2049","2050","2051","2052","2053","2054","2055","2056","2057","2058","2059","2060","2061","2062","2063","2064","2065","2066","2067","2068","2069","2070","2071","2072"]

    # 测试代码2——修改初拉力并计算
    # # with open('./accounts.json', 'r') as f:
    # #     data = json.load(f)
    # # data['PTNS']['2001']['ITEMS'][0]["TENSION"] = 200000
    # # tension_json = {"Assign" : data['PTNS']}
    # # MidasAPI("PUT", "/db/PTNS", tension_json)
    # # response = MidasAPI("POST", "/doc/Anal", {})

    # 测试代码3——获取索力结果表格
    # eles = [2005, 2006, 2007]
    # POST_json = {
    #     "Argument": {
    #         "TABLE_NAME": "TrussForce",
    #         "TABLE_TYPE": "TRUSSFORCE",
    #         "EXPORT_PATH": "E:\\CAE\\model\\mgfl\\api\\Output2.json",
    #         "UNIT": {"FORCE": "kN", "DIST": "m"},
    #         "STYLES": {"FORMAT": "Fixed", "PLACE": 12},
    #         "COMPONENTS": ["Elem", "Load", "Stage", "Step", "Force-I", "Force-J"],
    #         "NODE_ELEMS": {"KEYS": [eles[0]]},
    #         "LOAD_CASE_NAMES": ["合计(CS)"],
    #         "OPT_CS": True,
    #     }
    # }
    # MidasAPI("POST", "/POST/TABLE", POST_json)
    with open(
        "Output2.json",
        "r",
        encoding="gbk",
        errors="ignore",
    ) as f:
        temp_json2 = f.read()
    extracted_string = re.search(r"(\"TrussForce\":+)(.+)}", temp_json2).group(0)
    temp_json2 = json.loads("{" + extracted_string)
    temp_value2 = truss_force_tablejson_to_table(temp_json2)
    step_name = temp_value2["Step"].iloc[-3]

    # 格式化阶段步骤名称
    ## 获取所有阶段的信息
    allstage = MidasAPI("GET", "/db/STAG", {})
    ## 获取最后一个阶段的信息
    last_step_information = list(allstage["STAG"].items())[-1]
    ## 获取最后一个阶段的名称
    stagename = last_step_information[-1]["NAME"]
    STAGE_STEP = f"{stagename}:{step_name}"
    print(STAGE_STEP)

import json
import pandas as pd
import winreg

def Pretension_Loads_json_to_excel(data, excel_file_path):
    
    
    # 整理数据
    rows = []
    for key, value in data['PTNS'].items():
        item = value['ITEMS'][0]
        row = {
            '单元号': key,
            'ID': item['ID'],
            '荷载工况名称': item['LCNAME'],
            '组名称': item['GROUP_NAME'],
            '张力': item['TENSION']
        }
        rows.append(row)

    # 创建 DataFrame
    df = pd.DataFrame(rows)

    # 保存为 Excel 文件
    df.to_excel(excel_file_path, index=False)

def Pretension_Loads_json_to_df(data):
    # 读取 JSON 文件

    # 整理数据
    rows = []
    for key, value in data['Assign'].items():
        item = value['ITEMS'][0]
        row = {
            '单元号': key,
            'ID': item['ID'],
            '荷载工况名称': item['LCNAME'],
            '组名称': item['GROUP_NAME'],
            '张力': item['TENSION']
        }
        rows.append(row)

    # 创建 DataFrame
    df = pd.DataFrame(rows)
    return df

def Pretension_Loads_df_to_json(df):

    # 将 DataFrame 转换为字典列表
    data_list = df.to_dict(orient='records')
    # 重新构建 JSON 数据结构
    ptns_dict = {}
    for item in data_list:
        key = item['单元号']
        sub_dict = {
            'ITEMS': [
                {
                    'ID': item['ID'],
                    'LCNAME': item['荷载工况名称'],
                    'GROUP_NAME': item['组名称'],
                    'TENSION': item['张力']
                }
            ]
        }
        ptns_dict[key] = sub_dict

    final_json = {'Assign': ptns_dict}
    return final_json

import pandas as pd


def truss_force_tablejson_to_table(json_data):
    data = json_data["TrussForce"]
    headers = data["HEAD"]
    df = pd.DataFrame(data["DATA"], columns=headers)
    return df




def Pretension_Loads_excel_to_json(excel_file_path, json_file_path):
    # 读取 Excel 文件
    df = pd.read_excel(excel_file_path)

    # 将 DataFrame 转换为字典列表
    data_list = df.to_dict(orient='records')

    # 重新构建 JSON 数据结构
    ptns_dict = {}
    for item in data_list:
        key = item['单元号']
        sub_dict = {
            'ITEMS': [
                {
                    'ID': item['ID'],
                    'LCNAME': item['荷载工况名称'],
                    'GROUP_NAME': item['组名称'],
                    'TENSION': item['张力']
                }
            ]
        }
        ptns_dict[key] = sub_dict

    final_json = {'Assign': ptns_dict}

    # 将数据写入 JSON 文件
    with open(json_file_path, 'w', encoding='utf - 8') as f:
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



if __name__ == "__main__":
    json_file_path = './target.json'
    excel_file_path ='result.xlsx'
    # json_to_excel(json_file_path, excel_file_path)
    Pretension_Loads_excel_to_json(excel_file_path, json_file_path)
    #value = data['PTNS'].get("2001")
    #item = value['ITEMS'][0]
    #
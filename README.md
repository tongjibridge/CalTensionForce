# CalTensionForce

## 项目简介
本项目是一个用于施工索力计算的工具，提供用户界面进行数据展示和计算操作，通过与MIDAS API交互获取索力数据并自动化迭代计算施工索力。

## 项目结构
- `api.py`: 包含与MIDAS API交互的类和方法。
- `tools.py`: 包含一些工具函数，用于数据处理和转换。
- `fonts/`: 存放字体文件。
- `midas_ui.py`: 主程序文件，包含用户界面的实现。

## 依赖库
- flet
- pandas
- json
- requests
- winreg
## 功能说明
- 获取索力数据: 通过点击“获取索力”按钮，从MIDAS API获取索力数据，并在表格中显示。
- 修改初始索力：
方法1：通过UI界面中的table直接修改
方法2：通过本地表格init_tension.xlsx修改
- 开始计算: 点击“开始计算”按钮，在弹出的对话框选择初始索力来源于init_tension.xlsx还是UI中的table，程序将数据转换为JSON格式，并调用compute_tension函数进行索力计算。

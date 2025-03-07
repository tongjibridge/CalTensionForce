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

## 使用指南
### 启动软件
在软件根目录下打开命令行，输入python main.py运行软件，成功运行将出现操作界面。

<img width="491" alt="image" src="https://github.com/user-attachments/assets/99d6e0c6-41bf-4feb-857c-e24f82aebab8" />

### 获取索力数据
点击 “获取初始信息” 按钮，软件将自动向 Midas Civil API 发送请求，获取索力数据，并将其存储于 init_tension.xlsx 文件，同时在软件界面的数据表格中展示，方便用户查看与分析.

<img width="491" alt="image" src="https://github.com/user-attachments/assets/b0255eae-10fe-4675-92e5-f38f2f014622" />

### 修改目标索力
软件提供两种方式修改目标索力：
(1)通过 UI 界面修改：在软件界面的数据表格中，用户可直接双击单元格进行编辑。编辑完成后，单元格失去焦点时，数据将自动更新。
(2)通过本地表格修改：用户可使用外部编辑器打开 init_tension.xlsx 文件，修改其中的索力数据。修改保存后，在软件中点击相关操作按钮（如 “开始计算” 前需重新选择数据源），软件会读取更新后的数据进行计算。

### 开始计算
在误差允许值(百分比）文本框中填入误差的阈值，点击 “开始计算” 按钮，软件将弹出如图 3所示的对话框，用户需选择初始索力数据源（init_tension.xlsx 或 UI 中的表格）。选定后，软件会将数据转换为 JSON 格式，并调用 compute_tension 函数开启索力计算。计算过程中，软件将依据设定的计算逻辑迭代调整索力，直至偏差百分比满足要求（默认偏差百分比阈值为 0.15%，用户可在界面输入框修改）或达到最大迭代次数 20 次。计算完成后，软件会在界面显示计算结果，包括单元号、目标索力、实际索力、偏差及偏差百分比等信息，并提示 “索力计算完成！”

<img width="491" alt="image" src="https://github.com/user-attachments/assets/68bc3114-193b-4899-a2ba-b01464107c60" />

<img width="490" alt="image" src="https://github.com/user-attachments/assets/dfa9698e-bbb6-432f-9655-b49ff97eaa8e" />


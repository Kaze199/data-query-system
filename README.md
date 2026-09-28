# 数据查询系统（Python 版）

![Platform](https://img.shields.io/badge/platform-Windows%207%20SP1%20%2F%208%20%2F%2010%20%2F%2011-0078D4?logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Version](https://img.shields.io/badge/version-v3.0.0-success)
![GUI](https://img.shields.io/badge/GUI-Tkinter-FF6F00?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-All%20Rights%20Reserved-lightgrey)

一款基于 Python + Tkinter 的 Windows 桌面数据查询工具，可直接连接 **Access（.mdb / .accdb）** 与 **SQL Server** 数据库，提供数据查询、在线编辑、撤回、保存和 CSV 导出功能。开箱即用，**无需安装 Python 环境**。

---

## 目录

- [功能特性](#功能特性)
- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [使用指南](#使用指南)
- [从源码运行](#从源码运行)
- [打包为 EXE](#打包为-exe)
- [项目结构](#项目结构)
- [技术实现](#技术实现)
- [注意事项](#注意事项)
- [更新日志](#更新日志)

---

## 功能特性

- **双数据源支持**
  - Access 数据库：`.mdb` / `.accdb`，自动尝试 ACE 与 Jet 驱动
  - SQL Server：支持 Windows 集成身份验证与 SQL 账号登录，自动依次尝试 ODBC Driver 17 / 13、Native Client 11、SQL Server 驱动
- **两种查询方式**
  - 关键词搜索：在表内**所有字段**中模糊匹配（自动跳过二进制字段）
  - 字段值过滤：指定字段进行精确筛选
  - 可设置返回条数上限（默认 1000 条）
- **数据编辑**
  - 双击单元格即可带入列名与当前值
  - 修改先在界面生效，支持逐步**撤回**
  - 确认后一键写入数据库（带二次确认，避免误操作）
- **CSV 导出**：查询结果一键导出，采用 `UTF-8 BOM` 编码，Excel 直接打开不乱码
- **零依赖运行**：自带纯 ctypes 实现的 ODBC 封装层，无需安装 pyodbc；打包后为单文件 EXE

## 系统要求

| 项目 | 要求 |
|---|---|
| 操作系统 | Windows 7 SP1（需安装 [KB2533623](https://support.microsoft.com/help/2533623)）/ Windows 8 / 10 / 11 |
| Access 驱动 | 连接 Access 时需安装 [Microsoft Access Database Engine](https://learn.microsoft.com/office/troubleshoot/access/jet-odbc-driver-availability) |
| SQL Server 驱动 | 连接 SQL Server 时建议安装 [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server) |

## 快速开始

1. 前往 [Releases](https://github.com/Kaze199/data-query-system/releases) 页面下载最新版本
2. 根据系统选择程序，**双击即可运行**，无需安装：
   - Windows 7：`数据查询系统-Win7.exe`
   - Windows 10 / 11：`数据查询系统.exe`
3. 点击「选择数据库」连接 Access，或点击「SQL Server」填写服务器信息

## 使用指南

### 1. 连接数据库

- **Access**：点击「选择数据库」，选中 `.mdb` 或 `.accdb` 文件
- **SQL Server**：点击「SQL Server」，输入服务器地址与数据库名，选择身份验证方式后连接

### 2. 查询数据

1. 在「数据表」下拉框中选择表
2. （可选）输入「关键词」——将在所有字段中搜索
3. （可选）选择「字段」并填写「字段值」进行过滤
4. 设置「最多」返回条数，点击「查询」

### 3. 编辑与保存

1. **双击**需要修改的单元格，列名和当前值会自动填入编辑区
2. 修改「新值」后点击「应用修改」（仅修改界面内容）
3. 可点击「撤回」逐步撤销
4. 确认无误后点击「保存到数据库」，经二次确认后写入数据库

### 4. 导出 CSV

点击「导出CSV」，选择保存位置即可。文件名默认包含表名与时间戳。

## 从源码运行

环境要求：Windows + Python 3.8 及以上（[python.org](https://www.python.org/downloads/) 官方安装包已内置 Tkinter）。

```powershell
git clone https://github.com/Kaze199/data-query-system.git
cd data-query-system
python main.py
```

> 本项目通过内置的 `odbc_lite` 模块直接调用系统 `odbc32.dll`，**无需 `pip install` 任何第三方包**即可运行（数据库端的 ODBC 驱动仍需按上文安装）。

## 打包为 EXE

使用 PyInstaller 打包为单文件可执行程序：

```powershell
pip install pyinstaller
pyinstaller 数据查询系统-Win7.spec
```

生成的 EXE 位于 `dist/` 目录。Win7 版本的 spec 会额外打包 `ucrtbase.dll` 以兼容未更新通用 C 运行时的系统。

## 项目结构

```
data-query-system/
├── main.py                  # 主程序：Tkinter 界面与业务逻辑
├── odbc_lite.py             # 纯 ctypes ODBC 封装（pyodbc 兼容接口）
├── 数据查询系统-Win7.spec    # PyInstaller 打包配置（Win7 兼容版）
├── 使用说明.txt              # 软件内置使用说明
├── wheels/                  # 预留的 ODBC 驱动 wheel
└── README.md
```

## 技术实现

- **odbc_lite**：通过 `ctypes` 直接调用 Windows 自带的 `odbc32.dll`，实现了连接管理、语句执行、参数绑定、结果集读取、事务提交/回滚等功能，接口与 pyodbc 兼容，因此程序可在无第三方依赖的环境下运行。
- **方言适配**：针对 Access（Jet SQL）与 SQL Server（T-SQL）的差异，程序对标识符转义、空值转换、类型判断、表/主键读取等分别做了处理。
- **安全更新**：所有编辑均通过参数化语句（`?` 占位符）执行，表名/列名经过方括号转义，规避 SQL 注入风险。

## 注意事项

- 点击「应用修改」后数据仅在界面变更，**必须点击「保存到数据库」才会真正写入**
- 保存功能要求数据表具有主键；Access 表无法识别主键时默认以首列定位
- 修改生产数据库前建议先备份
- 如遇连接失败，请优先检查对应的 ODBC 驱动是否已正确安装

## 更新日志

### v3.0.0

- Python 重写并使用 PyInstaller 打包，免安装 Python 环境即可运行
- 支持 Access 与 SQL Server 双数据源
- 提供关键词搜索、字段值过滤、在线编辑、撤回保存与 CSV 导出
- 内置纯 ctypes 版 ODBC 封装，零第三方运行时依赖
- 提供 Windows 7 兼容版本

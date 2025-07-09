# AI日报生成器

AI日报生成器是一款自动化工具，旨在帮助开发者根据Git提交记录快速生成每日开发报告。

## 创建虚拟环境

在项目根目录下运行以下命令来创建虚拟环境：

```bash
python -m venv venv
```

## 激活虚拟环境

在Windows上运行：
```bash
venv\Scripts\activate
```

在Unix或MacOS上运行：
```bash
source venv/bin/activate
```

## 安装

激活虚拟环境后，安装项目依赖：

```bash
pip install -r requirements.txt
```

## 运行

在虚拟环境里，运行主程序：

```bash
python main.py
```

## 打包

如需将应用打包为可执行文件，可以使用PyInstaller：

```bash
pyinstaller --onefile main.py
```

## 删除虚拟环境

当不再需要虚拟环境时，可以直接删除venv文件夹：

```bash
rm -rf venv
```

在Windows上：

```bash
rmdir /s /q venv
```

## 使用方法

启动应用后，你可以：

- 选择一个或多个Git仓库目录
- 加载指定日期的提交记录
- 根据作者过滤提交记录
- 生成、复制和导出报告

如需调用AI功能，确保已配置API密钥。
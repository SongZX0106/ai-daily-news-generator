## 激活虚拟环境
.\venv\Scripts\Activate.ps1

## 创建虚拟环境
python -m venv venv

## 删除虚拟环境
rm -rf venv

## 运行
python main.py

## 打包
pyinstaller --noconfirm --onefile --windowed main.py

## 安装
pip install -r requirements.txt


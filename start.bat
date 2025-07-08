@echo off
REM 激活虚拟环境
call daily_report_tool\\venv\\Scripts\\activate.bat

REM 启动日报自动生成器
python daily_report_tool\\main.py

REM 保持窗口打开
pause
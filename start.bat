@echo off
REM WuwaAI Windows 启动脚本

echo ========================================
echo   WuwaAI 鸣潮智能自动化助手
echo ========================================

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查环境
python --version || goto :error

REM 安装依赖 (如果需要)
REM pip install -r backend\requirements.txt

REM 启动后端
echo.
echo 启动 WuwaAI 后端...
echo 访问 http://localhost:8000 查看API文档
python backend\main.py

pause
goto :eof

:error
echo.
echo 错误: 请确保已安装 Python 3.11+
pause

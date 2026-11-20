::可以通过在total中调用此脚本，达到直接在当前窗口路径下打开cmd窗口的操作

::total中需要通过 %P%S 传入参数

:: 切换cmd为 utf-8 字符集
chcp 65001

@echo off
:: 设置变量延迟加载
setlocal enabledelayedexpansion

:: 扩充入参成为一个合法的路径,并去除两端的引号(如果有)
set srcDir=%~dp1
:: 如果路径结尾是符号\,则去除之
if "\" == "!srcDir:~-1!" (set srcDir=%srcDir:~0,-1%)

:: 切换到 %~dp0 路径下工作
cd /d "%~dp0"

python "%~dp0csDocBuildWithGitVersion.py" || pause

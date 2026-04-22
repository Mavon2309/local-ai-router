@echo off
cd /d "%~dp0\..\.."
py tests_v2.py
echo Exit Code: %errorlevel%
pause
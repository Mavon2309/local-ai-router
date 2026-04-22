@echo off
:menu
cls
echo ==============================
echo   LOCAL AI ROUTER LAUNCHER
echo ==============================
echo.
echo 1. Run Router
echo 2. Run Tests
echo 3. Run Tests V2
echo 4. Dashboard
echo 5. Exit
echo.
set /p choice=Enter choice (1-5): 

if "%choice%"=="1" goto router
if "%choice%"=="2" goto tests
if "%choice%"=="3" goto testsv2
if "%choice%"=="4" goto dashboard
if "%choice%"=="5" exit

goto menu

:router
cd /d "%~dp0\..\..\.."
py router_v3.py
pause
goto menu

:tests
cd /d "%~dp0\.."
py tests.py
pause
goto menu

:testsv2
cd /d "%~dp0\.."
py tests_v2.py
pause
goto menu

:dashboard
cd /d "%~dp0\.."
py dashboard.py
pause
goto menu
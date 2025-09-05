@echo off
color 0A
cls
echo ========================================================
echo     File Transfer Automation Tool
echo     %date% %time%
echo     User: %USERNAME%
echo ========================================================
echo.
cd /d "%~dp0"
echo Starting file transfer process...
echo.
:: Run the .exe file directly instead of using python
file_transfer_tool.exe
echo.
echo ========================================================
echo Process completed! Press any key to close this window.
echo ========================================================
pause > nul
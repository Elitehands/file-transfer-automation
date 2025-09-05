@echo off
color 0A
cls
echo ========================================================
echo     File Transfer Automation Tool - Client Demo
echo     Current Date: %date% %time%
echo     User: %USERNAME%
echo ========================================================
echo.
echo Starting file transfer process...
echo.
timeout /t 2 >nul
.\file_transfer_tool.exe
echo.
echo ========================================================
echo Demo completed! Press any key to view transferred files...
pause >nul
start explorer "G:\My Drive\status log"
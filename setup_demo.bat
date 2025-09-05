@echo off
echo ====== SETTING UP FILE TRANSFER AUTOMATION DEMO ======
echo Current Date: %date% %time%
echo User: %USERNAME%

REM Create base directories first
mkdir "mock_demo" 2>nul
mkdir "mock_demo\Z_content" 2>nul
mkdir "mock_demo\G_content" 2>nul

REM Create full directory structure
mkdir "mock_demo\Z_content\Quality Assurance(QA Common)" 2>nul
mkdir "mock_demo\Z_content\Quality Assurance(QA Common)\25.Product Status Log" 2>nul
mkdir "mock_demo\Z_content\Quality Assurance(QA Common)\3.Batch Documents" 2>nul
mkdir "mock_demo\Z_content\Quality Assurance(QA Common)\3.Batch Documents\TEST001" 2>nul
mkdir "mock_demo\Z_content\Quality Assurance(QA Common)\3.Batch Documents\TEST002" 2>nul
mkdir "mock_demo\G_content\My Drive" 2>nul
mkdir "mock_demo\G_content\My Drive\status log" 2>nul
mkdir "mock_demo\config" 2>nul
mkdir "mock_demo\logs" 2>nul

REM Create sample batch files
echo This is a sample document > "mock_demo\Z_content\Quality Assurance(QA Common)\3.Batch Documents\TEST001\document1.pdf"
echo This is a sample report > "mock_demo\Z_content\Quality Assurance(QA Common)\3.Batch Documents\TEST001\report.xlsx"
echo This is a sample specification > "mock_demo\Z_content\Quality Assurance(QA Common)\3.Batch Documents\TEST002\specifications.docx"

REM Map virtual drives
subst Z: "%CD%\mock_demo\Z_content"
subst G: "%CD%\mock_demo\G_content"

REM Create settings.json with proper formatting
echo {> "mock_demo\config\settings.json"
echo   "vpn": {>> "mock_demo\config\settings.json"
echo     "connection_name": "bbuk vpn",>> "mock_demo\config\settings.json"
echo     "max_retries": 1,>> "mock_demo\config\settings.json"
echo     "retry_delay": 2>> "mock_demo\config\settings.json"
echo   },>> "mock_demo\config\settings.json"
echo   "paths": {>> "mock_demo\config\settings.json"
echo     "remote_server": "Z:\\Quality Assurance(QA Common)",>> "mock_demo\config\settings.json"
echo     "excel_file": "Z:\\Quality Assurance(QA Common)\\25.Product Status Log\\Product status Log.xlsx",>> "mock_demo\config\settings.json"
echo     "batch_documents": "Z:\\Quality Assurance(QA Common)\\3.Batch Documents",>> "mock_demo\config\settings.json"
echo     "local_gdrive": "G:\\My Drive\\status log">> "mock_demo\config\settings.json"
echo   },>> "mock_demo\config\settings.json"
echo   "excel": {>> "mock_demo\config\settings.json"
echo     "filter_criteria": {>> "mock_demo\config\settings.json"
echo       "initials_column": "AJ",>> "mock_demo\config\settings.json"
echo       "initials_value": "PP",>> "mock_demo\config\settings.json"
echo       "release_status_column": "AK">> "mock_demo\config\settings.json"
echo     }>> "mock_demo\config\settings.json"
echo   },>> "mock_demo\config\settings.json"
echo   "notifications": {>> "mock_demo\config\settings.json"
echo     "enabled": false>> "mock_demo\config\settings.json"
echo   },>> "mock_demo\config\settings.json"
echo   "system": {>> "mock_demo\config\settings.json"
echo     "test_mode": true>> "mock_demo\config\settings.json"
echo   }>> "mock_demo\config\settings.json"
echo }>> "mock_demo\config\settings.json"

REM Create .env file with dummy credentials
echo # Demo credentials - not real> "mock_demo\.env"
echo VPN_PASSWORD=demopassword123>> "mock_demo\.env"
echo SMTP_USERNAME=demo@example.com>> "mock_demo\.env"
echo SMTP_PASSWORD=demosmtppass>> "mock_demo\.env"

REM Copy executable
copy dist\file_transfer_tool.exe mock_demo\ 2>nul

echo ====== DEMO SETUP COMPLETE ======
echo Z: drive mapped to %CD%\mock_demo\Z_content
echo G: drive mapped to %CD%\mock_demo\G_content
echo When finished, run cleanup_demo.bat
echo.
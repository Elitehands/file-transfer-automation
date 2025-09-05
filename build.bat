@echo off
echo Building File Transfer Automation...

echo Building Mock Version...
python -m PyInstaller src/main.py --onefile --name file_transfer_automation_mock --distpath dist/mock

echo Building Production Version...
python -m PyInstaller src/main.py --onefile --name file_transfer_automation_prod --distpath dist/prod

echo Build complete!
echo Mock exe: dist/mock/file_transfer_automation_mock.exe
echo Production exe: dist/prod/file_transfer_automation_prod.exe

pause
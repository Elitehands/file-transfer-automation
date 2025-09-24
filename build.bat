@echo off
echo Building File Transfer Automation...

echo Building Test Version...
python -m PyInstaller src/main.py --onefile --name file_transfer_automation_test --distpath dist/test

echo Building Production Version...
python -m PyInstaller src/main.py --onefile --name file_transfer_automation_prod --distpath dist/prod

echo Build complete!
echo Test exe: dist/test/file_transfer_automation_test.exe
echo Production exe: dist/prod/file_transfer_automation_prod.exe

pause
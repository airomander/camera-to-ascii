@echo off
cd /d "%~dp0"
echo Building CamASCII.exe ...
pyinstaller --onefile --noconsole --name CamASCII --clean src\main.py
echo Done! Exe at dist\CamASCII.exe
pause

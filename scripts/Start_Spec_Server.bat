@echo off
cd /d "%~dp0\.."
echo Starting Lenovo Spec Server...
start "" "%~dp0..\release\index.html"
cd /d "%~dp0\..\src\server"
python lenovo_spec_server.py
pause

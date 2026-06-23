@echo off
cd /d "%~dp0"
echo Starting Lenovo Spec Server...
start "" http://localhost:9527
python lenovo_spec_server.py
pause

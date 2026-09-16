@echo off
title MediSec Backend Server
cd /d "%~dp0backend"
call ..\venv\Scripts\activate
python app.py
pause
@echo off
title Auto Lead Generation System
color 0A
echo.
echo  ============================================
echo   INSTALLING DEPENDENCIES (one time only)
echo  ============================================
pip install fastapi uvicorn sqlalchemy requests jinja2 python-multipart 2>NUL || py -m pip install fastapi uvicorn sqlalchemy requests jinja2 python-multipart

echo.
echo  ============================================
echo   INITIALIZING DATABASE
echo  ============================================
python database.py 2>NUL || py database.py

echo.
echo  ============================================
echo   STARTING LEAD GENERATION SYSTEM
echo  ============================================
python main.py 2>NUL || py main.py

pause

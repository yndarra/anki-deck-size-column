@echo off
chcp 65001 >nul
rem Сборка dist\deck_size_column.ankiaddon для загрузки на AnkiWeb
cd /d "%~dp0"
py -3.12 build.py
pause

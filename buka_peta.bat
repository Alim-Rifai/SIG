@echo off
color 0a
title Menjalankan Server Django WebGIS
echo Menjalankan server Django... Silakan tunggu...
echo.

:: 1. MASUK KE DIREKTORI PROYEK SESUAI GAMBAR
cd /d "C:\Users\farra\SIG\WebGIS"

:: 2. JALANKAN SERVER OTOMATIS
python manage.py runserver

pause
@echo off
setlocal
set PY=C:\Users\GAORZ\AppData\Local\Programs\Python\Python313\python.exe
set GIT=E:\Git\cmd\git.exe
set DIR=E:\Deepseek-workspace\lottery_backend

cd /d "%DIR%"

%PY% fetch_lottery.py >> update.log 2>&1
if errorlevel 1 goto fail

%GIT% add lottery_data.json >> update.log 2>&1
%GIT% diff --cached --quiet
if not errorlevel 1 goto nochange

%GIT% commit -m "auto update %date%" >> update.log 2>&1
%GIT% push origin main >> update.log 2>&1
echo [%date% %time%] updated-and-pushed >> update.log
exit /b 0

:nochange
echo [%date% %time%] no-change >> update.log
exit /b 0

:fail
echo [%date% %time%] FETCH-FAILED >> update.log
exit /b 1

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

set RETRY=0
:push
%GIT% push origin main >> update.log 2>&1
if not errorlevel 1 goto pushed
set /a RETRY+=1
if %RETRY% geq 3 goto pushfail
ping -n 16 127.0.0.1 >nul
goto push

:pushed
echo [%date% %time%] updated-and-pushed >> update.log
exit /b 0

:pushfail
echo [%date% %time%] PUSH-FAILED >> update.log
exit /b 1

:nochange
echo [%date% %time%] no-change >> update.log
exit /b 0

:fail
echo [%date% %time%] FETCH-FAILED >> update.log
exit /b 1

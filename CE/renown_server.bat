@echo off
REM renown_server.bat - (re)start the Renown board server in WSL.
REM   renown_server.bat          start it (minimised window; close it to stop)
REM   renown_server.bat restart  wsl --shutdown first (picks up .wslconfig changes)
REM Server script lives in WSL at ~/renown/start.sh

if /i "%~1"=="restart" (
  echo Shutting down WSL...
  wsl --shutdown
  timeout /t 3 /nobreak >nul
)

start "Renown server" /min wsl.exe -- bash -lc "~/renown/start.sh"
timeout /t 3 /nobreak >nul
powershell -NoProfile -Command "try{ $r=Invoke-WebRequest -UseBasicParsing http://localhost:8000/ -TimeoutSec 5; 'Renown server up: http://localhost:8000' }catch{ 'Server not answering yet - check the minimised Renown server window' }"

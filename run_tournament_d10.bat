@echo off
REM ============================================================================
REM Renown d10 tournament runner  —  CE build
REM
REM   C:\Users\Matt\OneDrive\Desktop\Game\CE\           <- this tree, self-contained
REM   C:\Users\Matt\OneDrive\Desktop\Game\Combatv3\     <- d6 build, NEVER touched
REM
REM CE imports nothing from Combatv3. Output goes to CE\lab_out\<TAG>\.
REM All paths derive from this file's location (%~dp0), so CE can be moved freely.
REM ============================================================================
setlocal
cd /d "%~dp0"

REM --- Interpreter (needs numpy, pandas, pyarrow, numba) ---
set PY="C:\Users\Matt\AppData\Local\Programs\Python\Python39\python.exe"
REM Conda alternative:
REM set PY="C:\Users\Matt\anaconda3\envs\kotr\python.exe"

REM ============================ DICE SETTINGS =================================
REM FACES   : die size. 10 for this build.
REM FOCUSED : natural result Focused fires on. 10 = nat-max only, 9 = top two faces.
REM FAT_S   : Fatigue token penalty to Strike (magnitude).
REM FAT_M   : Fatigue token penalty to Morale (magnitude).
REM PARRY   : base Parry target.
REM RECOVER : worst rung of the Recover ladder.
REM AUTOPASS: blank keeps the auto-pass rule; set to 1 to delete it.
set FACES=10
set FOCUSED=10
set FAT_S=2
set FAT_M=2
set PARRY=8
set RECOVER=8
set AUTOPASS=
REM set FACES=8
REM set FOCUSED=8
REM set FAT_S=1
REM set FAT_M=1
REM set PARRY=7
REM set RECOVER=8
REM set AUTOPASS=
REM TAG: subfolder under lab_out. Blank = auto-named from the dice settings.
set TAG=

REM ============================ POOL SETTINGS =================================
set MPC_MIN=1
set MPC_MAX=8
set RUNS=100
REM BALANCED=1 -> balanced_validation_pool ; BALANCED=0 -> archetype_pool
set BALANCED=1
set PER_CELL=100
set STRATIFY=250
set BUDGET_METRIC=total

REM ============================ MEMORY SETTINGS ===============================
REM WORKERS: each initializes numba and RESERVES several GB of Windows COMMIT.
REM Keep at 6-8. Lower on MemoryError; raise cautiously.
set WORKERS=6
set RENOWN_MEM_DEBUG=1
set SLOT_BUDGET=auto
REM ============================================================================

REM Exported so spawned workers inherit the same dice settings.
set RENOWN_PARRY_BASE=%PARRY%
set RENOWN_RECOVER_BASE=%RECOVER%

set NO_PLAYSTYLE=--no-playstyle

set DICE=--faces %FACES% --focused %FOCUSED% --fatigue-strike %FAT_S% --fatigue-morale %FAT_M%
if not "%AUTOPASS%"=="" set DICE=%DICE% --no-auto-pass
if not "%TAG%"==""      set DICE=%DICE% --tag %TAG%

echo Verifying CE wiring...
%PY% verify_d10.py
if errorlevel 1 (
  echo.
  echo VERIFY FAILED - not starting the run. Fix the errors above.
  pause
  exit /b 1
)
echo.

if "%BALANCED%"=="1" (
  %PY% run_tournament_d10.py %DICE% --balanced --mpc-min %MPC_MIN% --mpc-max %MPC_MAX% --per-cell %PER_CELL% --runs %RUNS% --slot-budget %SLOT_BUDGET% --workers %WORKERS% %NO_PLAYSTYLE%
) else (
  %PY% run_tournament_d10.py %DICE% --mpc-min %MPC_MIN% --mpc-max %MPC_MAX% --stratify %STRATIFY% --budget-metric %BUDGET_METRIC% --runs %RUNS% --slot-budget %SLOT_BUDGET% --workers %WORKERS% %NO_PLAYSTYLE%
)

echo.
echo Done. Output in "%~dp0lab_out"
pause
endlocal

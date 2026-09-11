@echo off
REM Fixed-gauntlet power-level run — tests EVERY build vs a fixed panel (linear, fast).
cd /d "C:\Users\Matt\OneDrive\Desktop\Game\Combatv3"

set MPC_MIN=4
set MPC_MAX=13
set GAUNTLET=80
set RUNS=60
REM PER_CELL: "none" = full detiered pool (~20210 builds, still fast via gauntlet); or an int to cap.
set PER_CELL=none

python gauntlet_run.py --balanced --mpc-min %MPC_MIN% --mpc-max %MPC_MAX% --per-cell %PER_CELL% --gauntlet %GAUNTLET% --runs %RUNS%

echo.
echo Done. Press any key to close.
pause

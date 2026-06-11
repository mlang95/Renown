@echo off
REM Renown tournament runner — edit the values below, then double-click or run from cmd.
cd /d "C:\Users\Matt\OneDrive\Desktop\Game\Combatv3"

REM --- Edit these ---
set MPC_MIN=3
set MPC_MAX=20
set RUNS=50

REM POOL MODE:
REM   BALANCED=1  -> balanced_validation_pool (all tiers, full gear cross, balanced per retinue x MPC)
REM   BALANCED=0  -> archetype_pool generator (realistic floors/caps)
set BALANCED=0
REM PER_CELL: balanced mode only. "none" = full pool (~27k builds, heavy); or an integer to cap each cell (e.g. 70).
set PER_CELL=100
REM STRATIFY: generator mode only (ignored when BALANCED=1). builds per budget bucket, or "all".
set STRATIFY=250
REM BUDGET_METRIC: generator mode only. "mpc" = pursuit count minus Efficient-X discounts;
REM "total" = raw pursuit count (matches the notebook's total_investment axis).
set BUDGET_METRIC=total

REM ============================ MEMORY SETTINGS ============================
REM WORKERS: parallel processes. EACH worker initializes numba, which RESERVES several GB of
REM Windows COMMIT (virtual memory) — even though physical RAM stays low. 14 workers reserved
REM ~112 GB of commit and exhausted the 128 GB commit limit (that was the MemoryError, NOT a lack
REM of physical RAM). Keep this at 6-8. Lower if you still hit MemoryError; raise cautiously.
set WORKERS=15
REM SLOT_BUDGET: batch memory budget (slots per block). "auto" sizes from free RAM (safe default).
REM   Or an integer: bigger = faster but more memory. Lower (e.g. 80000) if you hit MemoryError.
set SLOT_BUDGET=auto
REM ========================================================================
set NO_PLAYSTYLE=--no-playstyle
if "%BALANCED%"=="1" (
  python run_tournament.py --balanced --mpc-min %MPC_MIN% --mpc-max %MPC_MAX% --per-cell %PER_CELL% --runs %RUNS% --slot-budget %SLOT_BUDGET% --workers %WORKERS% %NO_PLAYSTYLE%
) else (
  python run_tournament.py --mpc-min %MPC_MIN% --mpc-max %MPC_MAX% --stratify %STRATIFY% --budget-metric %BUDGET_METRIC% --runs %RUNS% --slot-budget %SLOT_BUDGET% --workers %WORKERS% %NO_PLAYSTYLE%
)

echo.
echo Done. Press any key to close.
pause
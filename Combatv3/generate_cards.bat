@echo off
REM Renown card generator — regenerates every deck from renown_data.py.
REM Edit the values below, then double-click or run from cmd.
cd /d "C:\Users\Matt\OneDrive\Desktop\Game\Combatv3"

REM --- Edit these ---
REM MODE: renown (all 105 pursuits + factions + tactics + equipment)
REM       escalation (24-node combat subset + tactics + equipment; no factions)
REM       both (generate both sets)
set MODE=both

REM OUT_DIR: where the PDFs land
set OUT_DIR=cards

REM ONLY: restrict decks for a quick reprint, comma-separated, or "all".
REM       valid: pursuits, factions, tactics, equipment
set ONLY=all

REM -------------------------------------------------------------------
if /i "%ONLY%"=="all" (set ONLY_ARG=) else (set ONLY_ARG=--only %ONLY%)

if /i "%MODE%"=="both" (
  python -c "import sys; sys.argv=['x']; from generate_cards import generate_cards; o='%ONLY%'; only=None if o=='all' else [s.strip() for s in o.split(',')]; generate_cards(mode='renown', out_dir=r'%OUT_DIR%', only=only); generate_cards(mode='escalation', out_dir=r'%OUT_DIR%', only=only)"
) else (
  python -c "import sys; sys.argv=['x']; from generate_cards import generate_cards; o='%ONLY%'; only=None if o=='all' else [s.strip() for s in o.split(',')]; generate_cards(mode='%MODE%', out_dir=r'%OUT_DIR%', only=only)"
)

echo.
echo Done. Press any key to close.
pause

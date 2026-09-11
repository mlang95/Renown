@echo off
REM ============================================================================
REM  build_all.bat — regenerate everything downstream of renown_data.py.
REM  Cards (with player-scaled copies) and/or the Word docs. One double-click.
REM  Does NOT run tournaments — that's run_tournament.bat, kept separate.
REM ============================================================================
cd /d "C:\Users\Matt\OneDrive\Desktop\Game\Combatv3"
REM ---------------------------------------------------------------- EDIT THESE
REM MODE : renown | escalation | both
set MODE=both
REM WHAT : cards | docs | wiki | both
REM        cards = pursuit/faction/tactic/equipment PDFs
REM        docs  = Compendium.docx + Rules.docx (rebuilt from renown_data)
REM        wiki  = regenerate + push the GitHub Pages wiki (runs on docs/both too)
set WHAT=both
REM PLAYERS : table size (2-7). Scales pursuit copies by spec-tree fan-out:
REM           copies = fan_out + (PLAYERS-2), capped 2xPLAYERS; Monuments always 1.
set PLAYERS=1
REM OUT_DIR : where card PDFs land
set OUT_DIR=cards
REM WIKI_REPO : local clone of the RenownWiki repo (GitHub Pages source)
set WIKI_REPO=C:\Users\Matt\OneDrive\Desktop\Game\RenownWiki
REM PUSH_WIKI : 1 = git commit+push after build, 0 = build only (no push)
set PUSH_WIKI=1
REM ---------------------------------------------------------------------------
echo.
echo === build_all : MODE=%MODE%  WHAT=%WHAT%  PLAYERS=%PLAYERS% ===
echo.
if /i "%WHAT%"=="cards" goto cards
if /i "%WHAT%"=="docs"  goto docs
if /i "%WHAT%"=="wiki"  goto wiki
if /i "%WHAT%"=="both"  goto cards
echo Invalid WHAT=%WHAT% (use cards^|docs^|wiki^|both) & goto end
:cards
echo --- Cards ---
if /i "%MODE%"=="both" (
  python generate_cards.py renown "%OUT_DIR%" %PLAYERS%
  python generate_cards.py escalation "%OUT_DIR%" %PLAYERS%
) else (
  python generate_cards.py %MODE% "%OUT_DIR%" %PLAYERS%
)
if /i "%WHAT%"=="cards" goto end
:docs
echo --- Docs ---
echo   Compendium...
python gen_compendium.py compendium_data.json
python build_compendium.py compendium_data.json Compendium.docx
echo   Rules (filling table/glossary markers)...
python build_docs.py Rules_authored.docx Rules.docx
echo   FAQ (bot lookup + faction/equipment tables)...
python faq_export.py "ask-the-bot\renown_faq.txt"
:wiki
echo --- Wiki ---
rmdir /s /q wiki 2>nul
python build_wiki.py RULES.md wiki
if errorlevel 1 (
  echo   Wiki build FAILED — skipping push.
  goto end
)
if "%PUSH_WIKI%"=="0" (
  echo   Built wiki\ (push skipped: PUSH_WIKI=0^).
  goto end
)
if not exist "%WIKI_REPO%\.git" (
  echo   ERROR: %WIKI_REPO% is not a git repo. Clone RenownWiki there first:
  echo     git clone https://github.com/mlang95/RenownWiki.git "%WIKI_REPO%"
  goto end
)
echo   Syncing into %WIKI_REPO% ...
for /d %%D in ("%WIKI_REPO%\*") do if /i not "%%~nxD"==".git" rmdir /s /q "%%D" 2>nul
for %%F in ("%WIKI_REPO%\*") do if /i not "%%~nxF"==".git" del /q "%%F" 2>nul
xcopy /e /i /y /h wiki "%WIKI_REPO%" >nul
echo   Pushing to GitHub Pages ...
pushd "%WIKI_REPO%"
git add -A
git commit -m "wiki rebuild %date% %time%"
git push
popd
goto end
:end
echo.
echo Done. Press any key to close.
pause
#!/usr/bin/env bash
# start_public.sh — run the public side of Renown from the alpha checkout (WSL).
#   bash /mnt/c/Users/Matt/Renown-alpha-data/start_public.sh
# promote_alpha.bat keeps this copy (next to the live data, outside git) up to date.
#
# Board server: serves the alpha folder's board; live games stay in Renown-alpha-data (never in git).
#               Runs in the background (log: server.log); running this script again restarts it.
# Discord bot:  pulls, then runs with RENOWN_CE_ROOT on the alpha folder, so !ask and !renown serve
#               the alpha build, not whatever you last built in Desktop/Game. Ctrl+C stops the bot.
# PORT, RENOWN_TOKEN, RENOWN_DUKE_PIN, ... pass through from your shell as before.
ALPHA=/mnt/c/Users/Matt/Renown-alpha
DATA=/mnt/c/Users/Matt/Renown-alpha-data
BOT="$HOME/Github/discordBot-2.0"

if [ -f "$DATA/server.pid" ] && kill -0 "$(cat "$DATA/server.pid")" 2>/dev/null; then
  kill "$(cat "$DATA/server.pid")" && sleep 1 && echo "stopped the previous board server"
fi
mkdir -p "$DATA/games"
cd "$ALPHA/CE/references" || { echo "no alpha folder at $ALPHA - run promote_alpha.bat init"; exit 1; }
RENOWN_DB="$DATA/renown.db" RENOWN_GAMES="$DATA/games" nohup python3 server.py >> "$DATA/server.log" 2>&1 &
echo $! > "$DATA/server.pid"
echo "board server: pid $(cat "$DATA/server.pid"), port ${PORT:-8000}, log $DATA/server.log"

cd "$BOT" || { echo "no bot at $BOT"; exit 1; }
git pull https://github.com/mlang95/discordBot-2.0
RENOWN_CE_ROOT="$ALPHA/CE" python3 main.py

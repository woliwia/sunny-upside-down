#!/bin/zsh
# Double-click this file to start Sunny Upside Down 🍳☀️
# It serves the app at http://localhost:7777 and opens your browser.
# Keep this window open while you use the app; close it (Ctrl+C) to stop.

cd "$(dirname "$0")"
( sleep 1 && open "http://localhost:7777" ) &
exec python3 serve.py 7777

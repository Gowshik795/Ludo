#!/bin/bash
set -e

# MODE=x11 -> draw on the host's X11 display (Linux / XQuartz / WSLg)
if [ "$MODE" = "x11" ]; then
    exec python3 /app/ludo.py
fi

# Default MODE=web -> virtual screen + VNC + noVNC (play in the browser)
export DISPLAY=:99
Xvfb :99 -screen 0 1024x720x24 >/dev/null 2>&1 &
sleep 1
x11vnc -display :99 -forever -shared -nopw -quiet -rfbport 5900 >/dev/null 2>&1 &
websockify --web /usr/share/novnc 6080 localhost:5900 >/dev/null 2>&1 &

echo "Ludo is running -> open http://localhost:6080/vnc.html?autoconnect=true&resize=scale"
exec python3 /app/ludo.py

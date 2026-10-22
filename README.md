# Ludo (2 Players)

A two-player Ludo game (Red vs Yellow) written in Python with `tkinter`.

## Rules
- Roll a **6** to bring a token out of the yard.
- A 6, a capture, or bringing a token home gives an **extra turn**. Three 6s in a row lose the turn.
- Landing on an opponent captures it, except on safe squares (start squares and ★).
- An **exact roll** is needed to reach the home triangle.
- First player to bring all 4 tokens home wins.

Controls: `Space` or the button to roll, click a highlighted token to move it.

## Run locally (no Docker)
```bash
python ludo.py
```
Linux may need: `sudo apt install python3-tk`

## Run with Docker

### Option 1 - In your browser (works on Windows, macOS, Linux)
```bash
docker compose up --build
```
Then open: <http://localhost:6080/vnc.html?autoconnect=true&resize=scale>

Both players share the same window (hot-seat play).

### Option 2 - Native window on Linux (X11)
```bash
xhost +local:docker
docker compose --profile x11 up --build ludo-x11
```
On macOS you can do this with XQuartz; on Windows 11, WSLg works.

### Plain docker commands
```bash
docker build -t ludo .
docker run --rm -p 6080:6080 ludo
```

## Project layout
```
ludo.py              the game
Dockerfile           image (Ubuntu + tkinter + Xvfb + noVNC)
entrypoint.sh        starts the virtual screen and the game
docker-compose.yml   browser mode + optional X11 mode
```

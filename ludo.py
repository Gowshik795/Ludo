"""
Two-player Ludo (Red vs Yellow) built with Python's standard tkinter library.
No extra packages needed.  Run:  python ludo.py

Rules implemented
-----------------
* Each player has 4 tokens.  Roll a 6 to bring a token out of the yard.
* Rolling a 6, capturing an opponent, or bringing a token home gives an extra turn.
* Three 6s in a row forfeits the turn.
* Tokens landing on an opponent (outside safe squares) send it back to the yard.
* Safe squares (start squares and starred squares) cannot be captured on.
* A token needs an exact roll to reach the home triangle.
* First player to bring all 4 tokens home wins.
"""
import random
import tkinter as tk
from tkinter import messagebox

CELL = 40
BOARD = CELL * 15

COLORS = {"red": "#e53935", "green": "#43a047", "yellow": "#fdd835", "blue": "#1e88e5"}
PALE = {"red": "#ffcdd2", "green": "#c8e6c9", "yellow": "#fff59d", "blue": "#bbdefb"}

# The 52 squares of the main loop, clockwise, starting at Red's start square.
TRACK = [
    (1, 6), (2, 6), (3, 6), (4, 6), (5, 6),
    (6, 5), (6, 4), (6, 3), (6, 2), (6, 1), (6, 0),
    (7, 0), (8, 0),
    (8, 1), (8, 2), (8, 3), (8, 4), (8, 5),
    (9, 6), (10, 6), (11, 6), (12, 6), (13, 6), (14, 6),
    (14, 7), (14, 8),
    (13, 8), (12, 8), (11, 8), (10, 8), (9, 8),
    (8, 9), (8, 10), (8, 11), (8, 12), (8, 13), (8, 14),
    (7, 14), (6, 14),
    (6, 13), (6, 12), (6, 11), (6, 10), (6, 9),
    (5, 8), (4, 8), (3, 8), (2, 8), (1, 8), (0, 8),
    (0, 7), (0, 6),
]

# Players: Red (top-left) and Yellow (bottom-right) sit opposite each other.
PLAYERS = [
    {"name": "Red", "color": "red", "start": 0},
    {"name": "Yellow", "color": "yellow", "start": 26},
]

START_SQUARES = {0, 13, 26, 39}
STAR_SQUARES = {8, 21, 34, 47}
SAFE = START_SQUARES | STAR_SQUARES

# Progress of a token:  -1 = in yard, 0..50 = on main loop (0 = its start square),
# 51..55 = home column, 56 = home (finished).
YARD, LAST_TRACK, HOME = -1, 50, 56

YARD_SLOTS = {  # cell-coordinates (float) of the 4 yard circles per colour
    "red": [(1.5, 1.5), (3.5, 1.5), (1.5, 3.5), (3.5, 3.5)],
    "yellow": [(10.5, 10.5), (12.5, 10.5), (10.5, 12.5), (12.5, 12.5)],
}


def column_cell(player, step):
    """Home-column cell for step 0..4."""
    return (1 + step, 7) if player == 0 else (13 - step, 7)


class LudoGame:
    def __init__(self, root):
        self.root = root
        root.title("Ludo - 2 Players")
        root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=BOARD, height=BOARD, bg="#fafafa", highlightthickness=0)
        self.canvas.grid(row=0, column=0, padx=10, pady=10)

        side = tk.Frame(root, padx=10, pady=10)
        side.grid(row=0, column=1, sticky="n")
        self.turn_label = tk.Label(side, text="", font=("Helvetica", 18, "bold"), width=14)
        self.turn_label.pack(pady=(20, 10))
        self.dice_canvas = tk.Canvas(side, width=90, height=90, highlightthickness=0)
        self.dice_canvas.pack(pady=10)
        self.roll_btn = tk.Button(side, text="Roll Dice (Space)", font=("Helvetica", 13),
                                  width=16, command=self.roll)
        self.roll_btn.pack(pady=10)
        self.status = tk.Label(side, text="", font=("Helvetica", 11), wraplength=190,
                               justify="center", height=5)
        self.status.pack(pady=10)
        tk.Button(side, text="New Game", font=("Helvetica", 11), width=16,
                  command=self.new_game).pack(pady=(30, 0))
        tk.Label(side, text="Tip: click a highlighted\ntoken to move it.",
                 font=("Helvetica", 10), fg="#666").pack(pady=20)

        root.bind("<space>", lambda e: self.roll())
        self.new_game()

    # ------------------------------------------------------------------ state
    def new_game(self):
        self.tokens = [[YARD] * 4, [YARD] * 4]
        self.current = 0
        self.dice = 0
        self.sixes = 0
        self.movable = []
        self.phase = "roll"          # roll | move | busy | over
        self.set_status("Roll the dice to begin!")
        self.draw_dice(0)
        self.redraw()

    def set_status(self, text):
        self.status.config(text=text)

    def abs_index(self, player, progress):
        return (PLAYERS[player]["start"] + progress) % 52

    # ------------------------------------------------------------------- dice
    def roll(self):
        if self.phase != "roll":
            return
        self.phase = "busy"
        self.roll_btn.config(state="disabled")
        self.animate_roll(8)

    def animate_roll(self, frames):
        if frames > 0:
            self.draw_dice(random.randint(1, 6))
            self.root.after(60, lambda: self.animate_roll(frames - 1))
        else:
            self.dice = random.randint(1, 6)
            self.draw_dice(self.dice)
            self.after_roll()

    def after_roll(self):
        name = PLAYERS[self.current]["name"]
        self.sixes = self.sixes + 1 if self.dice == 6 else 0
        if self.sixes == 3:
            self.set_status(f"{name} rolled three 6s in a row - turn lost!")
            self.sixes = 0
            self.root.after(1200, self.next_turn)
            return

        self.movable = self.get_movable()
        if not self.movable:
            self.set_status(f"{name} rolled {self.dice} - no valid move.")
            self.root.after(1000, self.next_turn)
        elif len(self.movable) == 1:
            self.redraw()
            self.set_status(f"{name} rolled {self.dice} - only one move.")
            self.root.after(500, lambda: self.move_token(self.movable[0]))
        else:
            self.phase = "move"
            self.set_status(f"{name} rolled {self.dice}. Click a highlighted token.")
            self.redraw()

    def get_movable(self):
        result = []
        for i, p in enumerate(self.tokens[self.current]):
            if p == YARD:
                if self.dice == 6:
                    result.append(i)
            elif p + self.dice <= HOME:
                result.append(i)
        return result

    # ------------------------------------------------------------------ moves
    def on_token_click(self, player, idx):
        if self.phase == "move" and player == self.current and idx in self.movable:
            self.move_token(idx)

    def move_token(self, idx):
        player = self.current
        name = PLAYERS[player]["name"]
        p = self.tokens[player][idx]
        new = 0 if p == YARD else p + self.dice
        self.tokens[player][idx] = new
        self.movable = []
        extra = self.dice == 6
        msg = f"{name} moved a token."

        # Capture
        if 0 <= new <= LAST_TRACK and self.abs_index(player, new) not in SAFE:
            opp = 1 - player
            sq = self.abs_index(player, new)
            for j, q in enumerate(self.tokens[opp]):
                if 0 <= q <= LAST_TRACK and self.abs_index(opp, q) == sq:
                    self.tokens[opp][j] = YARD
                    extra = True
                    msg = f"{name} captured a {PLAYERS[opp]['name']} token!"

        if new == HOME:
            extra = True
            msg = f"{name} brought a token home!"

        self.redraw()

        if all(t == HOME for t in self.tokens[player]):
            self.phase = "over"
            self.set_status(f"{name} wins!")
            self.turn_label.config(text=f"{name} wins!")
            messagebox.showinfo("Game Over", f"{name} wins the game!")
            return

        if extra:
            self.set_status(msg + " Extra turn - roll again!")
            self.phase = "roll"
            self.roll_btn.config(state="normal")
        else:
            self.set_status(msg)
            self.root.after(500, self.next_turn)

    def next_turn(self):
        self.current = 1 - self.current
        self.sixes = 0
        self.movable = []
        self.phase = "roll"
        self.roll_btn.config(state="normal")
        self.set_status(f"{PLAYERS[self.current]['name']}'s turn - roll the dice.")
        self.redraw()

    # ---------------------------------------------------------------- drawing
    def draw_dice(self, value):
        c = self.dice_canvas
        c.delete("all")
        c.create_rectangle(5, 5, 85, 85, fill="white", outline="#333", width=3)
        layout = {
            1: [(1, 1)],
            2: [(0, 0), (2, 2)],
            3: [(0, 0), (1, 1), (2, 2)],
            4: [(0, 0), (2, 0), (0, 2), (2, 2)],
            5: [(0, 0), (2, 0), (1, 1), (0, 2), (2, 2)],
            6: [(0, 0), (2, 0), (0, 1), (2, 1), (0, 2), (2, 2)],
        }
        for gx, gy in layout.get(value, []):
            x, y = 22 + gx * 23, 22 + gy * 23
            c.create_oval(x - 7, y - 7, x + 7, y + 7, fill="#222")

    def rect(self, x, y, fill, w=1, outline="#555"):
        self.canvas.create_rectangle(x * CELL, y * CELL, (x + 1) * CELL, (y + 1) * CELL,
                                     fill=fill, outline=outline, width=w)

    def draw_board(self):
        c = self.canvas
        c.delete("all")

        # Yards
        yards = {"red": (0, 0), "green": (9, 0), "blue": (0, 9), "yellow": (9, 9)}
        active = {p["color"] for p in PLAYERS}
        for color, (x, y) in yards.items():
            on = color in active
            c.create_rectangle(x * CELL, y * CELL, (x + 6) * CELL, (y + 6) * CELL,
                               fill=COLORS[color] if on else "#cfcfcf", outline="#333", width=2)
            c.create_rectangle((x + 1) * CELL, (y + 1) * CELL, (x + 5) * CELL, (y + 5) * CELL,
                               fill="white", outline="#333")
            for sx, sy in [(1.5, 1.5), (3.5, 1.5), (1.5, 3.5), (3.5, 3.5)]:
                cx, cy = (x + sx) * CELL, (y + sy) * CELL
                c.create_oval(cx - 16, cy - 16, cx + 16, cy + 16,
                              fill=PALE[color] if on else "#e6e6e6", outline="#888")

        # Track squares
        for i, (x, y) in enumerate(TRACK):
            self.rect(x, y, "white")
        for idx, color in [(0, "red"), (13, "green"), (26, "yellow"), (39, "blue")]:
            x, y = TRACK[idx]
            self.rect(x, y, COLORS[color] if color in active else "#bdbdbd")
        for idx in STAR_SQUARES:
            x, y = TRACK[idx]
            c.create_text(x * CELL + 20, y * CELL + 20, text="\u2605", font=("Helvetica", 18), fill="#777")

        # Home columns
        for i in range(5):
            self.rect(1 + i, 7, COLORS["red"])
            self.rect(13 - i, 7, COLORS["yellow"])
            self.rect(7, 1 + i, "#bdbdbd")
            self.rect(7, 13 - i, "#bdbdbd")

        # Centre triangles
        l, t, r, b = 6 * CELL, 6 * CELL, 9 * CELL, 9 * CELL
        mx, my = 7.5 * CELL, 7.5 * CELL
        c.create_polygon(l, t, l, b, mx, my, fill=COLORS["red"], outline="#333")
        c.create_polygon(r, t, r, b, mx, my, fill=COLORS["yellow"], outline="#333")
        c.create_polygon(l, t, r, t, mx, my, fill="#bdbdbd", outline="#333")
        c.create_polygon(l, b, r, b, mx, my, fill="#bdbdbd", outline="#333")

    def token_pixel(self, player, idx):
        color = PLAYERS[player]["color"]
        p = self.tokens[player][idx]
        if p == YARD:
            fx, fy = YARD_SLOTS[color][idx]
            return fx * CELL, fy * CELL, 14
        if p <= LAST_TRACK:
            x, y = TRACK[self.abs_index(player, p)]
            return x * CELL + 20, y * CELL + 20, 14
        if p < HOME:
            x, y = column_cell(player, p - 51)
            return x * CELL + 20, y * CELL + 20, 14
        # Finished: tuck into own triangle
        fx = 6.6 if player == 0 else 8.4
        return fx * CELL, (6.6 + 0.6 * idx) * CELL, 8

    def redraw(self):
        self.draw_board()
        c = self.canvas
        color_name = PLAYERS[self.current]["color"]
        if self.phase != "over":
            self.turn_label.config(text=f"{PLAYERS[self.current]['name']}'s turn",
                                   fg=COLORS[color_name] if color_name != "yellow" else "#c9a800")

        # Group tokens by pixel so stacked tokens are spread a little
        spots = {}
        for pl in (0, 1):
            for i in range(4):
                x, y, r = self.token_pixel(pl, i)
                spots.setdefault((round(x), round(y)), []).append((pl, i, x, y, r))

        offsets = [(0, 0), (-8, -8), (8, 8), (-8, 8), (8, -8), (0, -10), (0, 10), (-10, 0)]
        for group in spots.values():
            for n, (pl, i, x, y, r) in enumerate(group):
                if len(group) > 1:
                    dx, dy = offsets[n % len(offsets)]
                    x, y, r = x + dx, y + dy, min(r, 10)
                color = COLORS[PLAYERS[pl]["color"]]
                highlight = (self.phase == "move" and pl == self.current and i in self.movable)
                tag = f"tok_{pl}_{i}"
                c.create_oval(x - r, y - r, x + r, y + r, fill=color,
                              outline="#000" if not highlight else "#00b0ff",
                              width=2 if not highlight else 4, tags=(tag,))
                c.create_oval(x - r / 2, y - r / 2, x + r / 2, y + r / 2,
                              fill="", outline="white", width=2, tags=(tag,))
                c.tag_bind(tag, "<Button-1>", lambda e, p=pl, k=i: self.on_token_click(p, k))
                if highlight:
                    c.tag_bind(tag, "<Enter>", lambda e: c.config(cursor="hand2"))
                    c.tag_bind(tag, "<Leave>", lambda e: c.config(cursor=""))


if __name__ == "__main__":
    root = tk.Tk()
    LudoGame(root)
    root.mainloop()

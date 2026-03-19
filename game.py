"""24 Game - Make 24 from 4 poker cards using +, -, *, /. GUI version."""

import itertools
import random
import re
import tkinter as tk
from tkinter import font as tkfont

SUITS = ["♠", "♥", "♦", "♣"]
SUIT_COLORS = {"♠": "#1F1F1F", "♣": "#1F1F1F", "♥": "#E41E3F", "♦": "#E41E3F"}
RANK_NAMES = {1: "A", 10: "10", 11: "J", 12: "Q", 13: "K"}

# Card dimensions
CARD_W = 120
CARD_H = 170
CARD_RADIUS = 12
CARD_PAD = 20
CARD_BG = "#FFFEF0"
TABLE_BG = "#0B6623"


class Card:
    def __init__(self, rank: int, suit: str):
        self.rank = rank
        self.suit = suit

    @property
    def value(self) -> int:
        return min(self.rank, 10)

    @property
    def rank_str(self) -> str:
        return RANK_NAMES.get(self.rank, str(self.rank))

    @property
    def display_name(self) -> str:
        return f"{self.rank_str}{self.suit}"


def build_deck() -> list[Card]:
    deck = [Card(rank, suit) for suit in SUITS for rank in range(1, 14)]
    random.shuffle(deck)
    return deck


# --- Solver ---

def _apply(op: str, x: float, y: float) -> float | None:
    if op == "+":
        return x + y
    if op == "-":
        return x - y
    if op == "*":
        return x * y
    if op == "/":
        return x / y if y != 0 else None
    return None


def can_make_24(values: list[int]) -> str | None:
    ops = ["+", "-", "*", "/"]
    for perm in itertools.permutations(values):
        a, b, c, d = [float(x) for x in perm]
        sa, sb, sc, sd = [str(x) for x in perm]
        for o1, o2, o3 in itertools.product(ops, repeat=3):
            r = _apply(o1, a, b)
            if r is not None:
                r2 = _apply(o2, r, c)
                if r2 is not None:
                    r3 = _apply(o3, r2, d)
                    if r3 is not None and abs(r3 - 24) < 1e-9:
                        return f"(({sa} {o1} {sb}) {o2} {sc}) {o3} {sd}"

            r = _apply(o2, b, c)
            if r is not None:
                r2 = _apply(o1, a, r)
                if r2 is not None:
                    r3 = _apply(o3, r2, d)
                    if r3 is not None and abs(r3 - 24) < 1e-9:
                        return f"({sa} {o1} ({sb} {o2} {sc})) {o3} {sd}"

            r1 = _apply(o1, a, b)
            r2 = _apply(o3, c, d)
            if r1 is not None and r2 is not None:
                r3 = _apply(o2, r1, r2)
                if r3 is not None and abs(r3 - 24) < 1e-9:
                    return f"({sa} {o1} {sb}) {o2} ({sc} {o3} {sd})"

            r = _apply(o2, b, c)
            if r is not None:
                r2 = _apply(o3, r, d)
                if r2 is not None:
                    r3 = _apply(o1, a, r2)
                    if r3 is not None and abs(r3 - 24) < 1e-9:
                        return f"{sa} {o1} (({sb} {o2} {sc}) {o3} {sd})"

            r = _apply(o3, c, d)
            if r is not None:
                r2 = _apply(o2, b, r)
                if r2 is not None:
                    r3 = _apply(o1, a, r2)
                    if r3 is not None and abs(r3 - 24) < 1e-9:
                        return f"{sa} {o1} ({sb} {o2} ({sc} {o3} {sd}))"
    return None


# --- Expression evaluation ---

def evaluate_expression(expr: str) -> float | None:
    if not re.match(r'^[\d\s\+\-\*/\(\)\.]+$', expr):
        return None
    try:
        result = eval(expr, {"__builtins__": {}}, {})  # noqa: S307
        return float(result)
    except (SyntaxError, TypeError, ZeroDivisionError, NameError):
        return None


def extract_numbers(expr: str) -> list[int]:
    return [int(x) for x in re.findall(r'\d+', expr)]


# --- GUI ---

def draw_rounded_rect(canvas: tk.Canvas, x1: int, y1: int, x2: int, y2: int,
                       r: int = 10, **kwargs) -> int:
    points = [
        x1 + r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def draw_card(canvas: tk.Canvas, x: int, y: int, card: Card) -> None:
    """Draw a single card at position (x, y) on the canvas."""
    color = SUIT_COLORS[card.suit]
    rank = card.rank_str
    suit = card.suit

    # Shadow
    draw_rounded_rect(canvas, x + 3, y + 3, x + CARD_W + 3, y + CARD_H + 3,
                      r=CARD_RADIUS, fill="#1a3d1a", outline="")

    # Card body
    draw_rounded_rect(canvas, x, y, x + CARD_W, y + CARD_H,
                      r=CARD_RADIUS, fill=CARD_BG, outline="#999999", width=1)

    # Top-left rank and suit
    canvas.create_text(x + 12, y + 14, text=rank, fill=color,
                       font=("Arial", 16, "bold"), anchor="n")
    canvas.create_text(x + 12, y + 34, text=suit, fill=color,
                       font=("Arial", 14), anchor="n")

    # Center suit (large)
    canvas.create_text(x + CARD_W // 2, y + CARD_H // 2, text=suit,
                       fill=color, font=("Arial", 48), anchor="center")

    # Bottom-right rank and suit (rotated via placement)
    canvas.create_text(x + CARD_W - 12, y + CARD_H - 14, text=rank,
                       fill=color, font=("Arial", 16, "bold"), anchor="s")
    canvas.create_text(x + CARD_W - 12, y + CARD_H - 34, text=suit,
                       fill=color, font=("Arial", 14), anchor="s")

    # Value label below the card
    canvas.create_text(x + CARD_W // 2, y + CARD_H + 14, text=f"= {card.value}",
                       fill="#CCCCCC", font=("Arial", 13, "bold"), anchor="n")


class Game:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("24 Game")
        self.root.configure(bg=TABLE_BG)
        self.root.resizable(False, False)

        self.deck: list[Card] = []
        self.hand: list[Card] = []
        self.values: list[int] = []
        self.solution: str | None = None
        self.score = 0
        self.rounds = 0

        self._build_ui()
        self._new_game()

    def _build_ui(self) -> None:
        # Header
        header = tk.Frame(self.root, bg=TABLE_BG)
        header.pack(fill="x", padx=20, pady=(15, 5))

        self.title_label = tk.Label(
            header, text="THE 24 GAME", bg=TABLE_BG, fg="#FFD700",
            font=("Arial", 22, "bold"),
        )
        self.title_label.pack()

        # Info bar
        info = tk.Frame(self.root, bg=TABLE_BG)
        info.pack(fill="x", padx=20, pady=(5, 5))

        self.score_label = tk.Label(
            info, text="Score: 0", bg=TABLE_BG, fg="white",
            font=("Arial", 14, "bold"),
        )
        self.score_label.pack(side="left")

        self.cards_left_label = tk.Label(
            info, text="Cards left: 52", bg=TABLE_BG, fg="white",
            font=("Arial", 14),
        )
        self.cards_left_label.pack(side="right")

        self.round_label = tk.Label(
            info, text="Round 0", bg=TABLE_BG, fg="white",
            font=("Arial", 14),
        )
        self.round_label.pack()

        # Card canvas
        canvas_w = CARD_W * 4 + CARD_PAD * 5
        canvas_h = CARD_H + 50
        self.canvas = tk.Canvas(
            self.root, width=canvas_w, height=canvas_h,
            bg=TABLE_BG, highlightthickness=0,
        )
        self.canvas.pack(padx=20, pady=10)

        # Status message
        self.status_label = tk.Label(
            self.root, text="", bg=TABLE_BG, fg="#CCCCCC",
            font=("Arial", 12),
        )
        self.status_label.pack(pady=(0, 5))

        # Expression input
        input_frame = tk.Frame(self.root, bg=TABLE_BG)
        input_frame.pack(padx=20, pady=5)

        self.entry = tk.Entry(
            input_frame, width=35, font=("Courier", 16),
            justify="center", bg="#1a3d1a", fg="white",
            insertbackground="white", relief="flat",
            highlightthickness=2, highlightcolor="#FFD700",
            highlightbackground="#2a5d2a",
        )
        self.entry.pack(ipady=6)
        self.entry.bind("<Return>", lambda e: self._submit())

        # Buttons
        btn_frame = tk.Frame(self.root, bg=TABLE_BG)
        btn_frame.pack(padx=20, pady=10)

        btn_style = {
            "font": ("Arial", 13, "bold"),
            "relief": "flat",
            "cursor": "hand2",
            "padx": 18,
            "pady": 6,
        }

        self.submit_btn = tk.Button(
            btn_frame, text="Submit", bg="#FFD700", fg="#1a1a1a",
            activebackground="#FFC300", command=self._submit, **btn_style,
        )
        self.submit_btn.pack(side="left", padx=5)

        self.skip_btn = tk.Button(
            btn_frame, text="Skip", bg="#555555", fg="white",
            activebackground="#777777", command=self._skip, **btn_style,
        )
        self.skip_btn.pack(side="left", padx=5)

        self.hint_btn = tk.Button(
            btn_frame, text="Hint (-1pt)", bg="#555555", fg="white",
            activebackground="#777777", command=self._hint, **btn_style,
        )
        self.hint_btn.pack(side="left", padx=5)

        # Feedback message
        self.feedback_label = tk.Label(
            self.root, text="", bg=TABLE_BG, fg="white",
            font=("Arial", 13), wraplength=500,
        )
        self.feedback_label.pack(pady=(0, 15))

    def _new_game(self) -> None:
        self.deck = build_deck()
        self.score = 0
        self.rounds = 0
        self._next_round()

    def _update_info(self) -> None:
        self.score_label.config(text=f"Score: {self.score}")
        self.round_label.config(text=f"Round {self.rounds}")
        self.cards_left_label.config(text=f"Cards left: {len(self.deck)}")

    def _draw_hand(self) -> None:
        self.canvas.delete("all")
        for i, card in enumerate(self.hand):
            x = CARD_PAD + i * (CARD_W + CARD_PAD)
            y = 10
            draw_card(self.canvas, x, y, card)

    def _next_round(self) -> None:
        if len(self.deck) < 4:
            self._game_over()
            return

        self.hand = [self.deck.pop() for _ in range(4)]
        self.values = [c.value for c in self.hand]
        self.solution = can_make_24(self.values)
        self.rounds += 1

        self._update_info()
        self._draw_hand()

        if self.solution:
            self.status_label.config(text="A solution exists!", fg="#90EE90")
        else:
            self.status_label.config(text="No solution possible.", fg="#FF9999")

        self.feedback_label.config(text="")
        self.entry.delete(0, "end")
        self.entry.focus_set()

    def _submit(self) -> None:
        expr = self.entry.get().strip()
        if not expr:
            return

        used = sorted(extract_numbers(expr))
        expected = sorted(self.values)

        if used != expected:
            self.feedback_label.config(
                text=f"Use exactly these values: {self.values}  (you used: {used})",
                fg="#FF9999",
            )
            return

        result = evaluate_expression(expr)
        if result is None:
            self.feedback_label.config(
                text="Invalid expression. Use numbers, +, -, *, /, and ().",
                fg="#FF9999",
            )
            return

        if abs(result - 24) < 1e-9:
            self.score += 1
            self.feedback_label.config(
                text=f"Correct! {expr} = 24  (+1 point)", fg="#90EE90",
            )
            self._update_info()
            self.root.after(1200, self._next_round)
        else:
            self.feedback_label.config(
                text=f"{expr} = {result:.4g}, not 24. Try again.", fg="#FF9999",
            )

    def _skip(self) -> None:
        if self.solution:
            self.score -= 1
            self.feedback_label.config(
                text=f"Solution was: {self.solution}  (-1 point)", fg="#FF9999",
            )
        else:
            self.feedback_label.config(
                text="Correct, no solution! No penalty.", fg="#90EE90",
            )
        self._update_info()
        self.root.after(1500, self._next_round)

    def _hint(self) -> None:
        if self.solution:
            self.score -= 1
            self.feedback_label.config(
                text=f"Hint: {self.solution}  (-1 point)", fg="#FFD700",
            )
            self._update_info()
        else:
            self.feedback_label.config(
                text="No solution exists for these cards.", fg="#FFD700",
            )

    def _game_over(self) -> None:
        self.canvas.delete("all")
        self.canvas.create_text(
            self.canvas.winfo_width() // 2, CARD_H // 2,
            text="GAME OVER", fill="#FFD700",
            font=("Arial", 36, "bold"), anchor="center",
        )
        self.status_label.config(text="")
        self.feedback_label.config(
            text=f"Final Score: {self.score} / {self.rounds} rounds",
            fg="white",
        )
        self.entry.config(state="disabled")
        self.submit_btn.config(state="disabled")
        self.skip_btn.config(state="disabled")
        self.hint_btn.config(state="disabled")

        # Add play again button
        self.play_again_btn = tk.Button(
            self.root, text="Play Again", bg="#FFD700", fg="#1a1a1a",
            font=("Arial", 13, "bold"), relief="flat", cursor="hand2",
            padx=18, pady=6, activebackground="#FFC300",
            command=self._restart,
        )
        self.play_again_btn.pack(pady=(0, 15))

    def _restart(self) -> None:
        self.play_again_btn.destroy()
        self.entry.config(state="normal")
        self.submit_btn.config(state="normal")
        self.skip_btn.config(state="normal")
        self.hint_btn.config(state="normal")
        self._new_game()


def main() -> None:
    root = tk.Tk()
    Game(root)
    root.mainloop()


if __name__ == "__main__":
    main()

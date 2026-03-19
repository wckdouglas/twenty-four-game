"""24 Game - Make 24 from 4 poker cards using +, -, *, /. GUI version."""

import itertools
import random
import re
import tkinter as tk

SUITS = ["♠", "♥", "♦", "♣"]
SUIT_COLORS = {"♠": "#1F1F1F", "♣": "#1F1F1F", "♥": "#E41E3F", "♦": "#E41E3F"}
RANK_NAMES = {1: "A", 10: "10", 11: "J", 12: "Q", 13: "K"}

CARD_W = 110
CARD_H = 155
CARD_RADIUS = 12
CARD_BG = "#FFFEF0"
TABLE_BG = "#0B6623"

OPS = ["+", "-", "*", "/"]

# Expression formatters for 5 parenthesization patterns
PAREN_FMTS = [
    lambda v, o: f"(({v[0]} {o[0]} {v[1]}) {o[1]} {v[2]}) {o[2]} {v[3]}",
    lambda v, o: f"({v[0]} {o[0]} ({v[1]} {o[1]} {v[2]})) {o[2]} {v[3]}",
    lambda v, o: f"({v[0]} {o[0]} {v[1]}) {o[1]} ({v[2]} {o[2]} {v[3]})",
    lambda v, o: f"{v[0]} {o[0]} (({v[1]} {o[1]} {v[2]}) {o[2]} {v[3]})",
    lambda v, o: f"{v[0]} {o[0]} ({v[1]} {o[1]} ({v[2]} {o[2]} {v[3]}))",
]

# Bracket arcs for each pattern: list of (left_card, right_card, level)
# level 0 = innermost (first evaluated), drawn closest to cards
BRACKET_ARCS = [
    # ((a o b) o c) o d
    [(0, 1, 0), (0, 2, 1), (0, 3, 2)],
    # (a o (b o c)) o d
    [(1, 2, 0), (0, 2, 1), (0, 3, 2)],
    # (a o b) o (c o d)
    [(0, 1, 0), (2, 3, 0), (0, 3, 1)],
    # a o ((b o c) o d)
    [(1, 2, 0), (1, 3, 1), (0, 3, 2)],
    # a o (b o (c o d))
    [(2, 3, 0), (1, 3, 1), (0, 3, 2)],
]

BRACKET_COLORS = ["#FFD700", "#4FC3F7", "#CE93D8"]  # gold, blue, purple per level


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
    ops_list = ["+", "-", "*", "/"]
    for perm in itertools.permutations(values):
        a, b, c, d = [float(x) for x in perm]
        sa, sb, sc, sd = [str(x) for x in perm]
        for o1, o2, o3 in itertools.product(ops_list, repeat=3):
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


def evaluate_expression(expr: str) -> float | None:
    if not re.match(r"^[\d\s\+\-\*/\(\)\.]+$", expr):
        return None
    try:
        result = eval(expr, {"__builtins__": {}}, {})  # noqa: S307
        return float(result)
    except (SyntaxError, TypeError, ZeroDivisionError, NameError):
        return None


# --- Canvas drawing helpers ---


def draw_rounded_rect(
    canvas: tk.Canvas, x1: int, y1: int, x2: int, y2: int, r: int = 10, **kwargs
) -> int:
    points = [
        x1 + r,
        y1,
        x2 - r,
        y1,
        x2,
        y1,
        x2,
        y1 + r,
        x2,
        y2 - r,
        x2,
        y2,
        x2 - r,
        y2,
        x1 + r,
        y2,
        x1,
        y2,
        x1,
        y2 - r,
        x1,
        y1 + r,
        x1,
        y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def draw_card_at(
    canvas: tk.Canvas, x: int, y: int, card: Card, tag: str = "", highlight: bool = False
) -> None:
    color = SUIT_COLORS[card.suit]
    rank = card.rank_str
    suit = card.suit

    draw_rounded_rect(
        canvas,
        x + 3,
        y + 3,
        x + CARD_W + 3,
        y + CARD_H + 3,
        r=CARD_RADIUS,
        fill="#1a3d1a",
        outline="",
        tags=tag,
    )
    outline_color = "#FFD700" if highlight else "#999999"
    outline_w = 3 if highlight else 1
    draw_rounded_rect(
        canvas,
        x,
        y,
        x + CARD_W,
        y + CARD_H,
        r=CARD_RADIUS,
        fill=CARD_BG,
        outline=outline_color,
        width=outline_w,
        tags=tag,
    )
    canvas.create_text(
        x + 12, y + 14, text=rank, fill=color, font=("Arial", 15, "bold"), anchor="n", tags=tag
    )
    canvas.create_text(
        x + 12, y + 33, text=suit, fill=color, font=("Arial", 13), anchor="n", tags=tag
    )
    canvas.create_text(
        x + CARD_W // 2,
        y + CARD_H // 2,
        text=suit,
        fill=color,
        font=("Arial", 44),
        anchor="center",
        tags=tag,
    )
    canvas.create_text(
        x + CARD_W - 12,
        y + CARD_H - 14,
        text=rank,
        fill=color,
        font=("Arial", 15, "bold"),
        anchor="s",
        tags=tag,
    )
    canvas.create_text(
        x + CARD_W - 12,
        y + CARD_H - 33,
        text=suit,
        fill=color,
        font=("Arial", 13),
        anchor="s",
        tags=tag,
    )
    canvas.create_text(
        x + CARD_W // 2,
        y + CARD_H + 12,
        text=f"= {card.value}",
        fill="#CCCCCC",
        font=("Arial", 12, "bold"),
        anchor="n",
        tags=tag,
    )


# --- Layout ---

OP_W = 50
SLOT_GAP = 10
MARGIN_X = 30
CARD_TOP = 15
BRACKET_TOP = CARD_TOP + CARD_H + 32  # where brackets start (below value labels)
BRACKET_SPACING = 28  # vertical space per bracket level
CANVAS_W = MARGIN_X * 2 + CARD_W * 4 + OP_W * 3 + SLOT_GAP * 6
CANVAS_H = BRACKET_TOP + BRACKET_SPACING * 3 + 10


def slot_x(i: int) -> int:
    return MARGIN_X + i * (CARD_W + SLOT_GAP + OP_W + SLOT_GAP)


def slot_center_x(i: int) -> int:
    return slot_x(i) + CARD_W // 2


def op_center_x(i: int) -> int:
    return slot_x(i) + CARD_W + SLOT_GAP + OP_W // 2


# --- Game ---


class Game:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("24 Game")
        self.root.configure(bg=TABLE_BG)
        self.root.resizable(False, False)

        self.deck: list[Card] = []
        self.hand: list[Card] = []
        self.solution: str | None = None
        self.score = 0
        self.rounds = 0

        self.ops: list[int] = [0, 0, 0]
        self.paren_idx = 0

        self._drag_idx: int | None = None
        self._drag_offset_x = 0
        self._drag_offset_y = 0

        self._build_ui()
        self._new_game()

    def _build_ui(self) -> None:
        # Header
        tk.Label(
            self.root, text="THE 24 GAME", bg=TABLE_BG, fg="#FFD700", font=("Arial", 22, "bold")
        ).pack(pady=(12, 2))

        # Info bar
        info = tk.Frame(self.root, bg=TABLE_BG)
        info.pack(fill="x", padx=20, pady=2)
        self.score_label = tk.Label(
            info, text="Score: 0", bg=TABLE_BG, fg="white", font=("Arial", 14, "bold")
        )
        self.score_label.pack(side="left")
        self.cards_left_label = tk.Label(
            info, text="Cards left: 52", bg=TABLE_BG, fg="white", font=("Arial", 14)
        )
        self.cards_left_label.pack(side="right")
        self.round_label = tk.Label(
            info, text="Round 0", bg=TABLE_BG, fg="white", font=("Arial", 14)
        )
        self.round_label.pack()

        # Instruction
        self.status_label = tk.Label(
            self.root, text="", bg=TABLE_BG, fg="#CCCCCC", font=("Arial", 11)
        )
        self.status_label.pack(pady=(2, 0))

        # Main canvas
        self.canvas = tk.Canvas(
            self.root, width=CANVAS_W, height=CANVAS_H, bg=TABLE_BG, highlightthickness=0
        )
        self.canvas.pack(padx=10, pady=(8, 0))
        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

        # Grouping selector: < [label] >
        group_frame = tk.Frame(self.root, bg=TABLE_BG)
        group_frame.pack(pady=(6, 2))

        arrow_style = {
            "font": ("Arial", 16, "bold"),
            "bg": "#2a5d2a",
            "fg": "#1a1a1a",
            "activebackground": "#3a7d3a",
            "activeforeground": "#1a1a1a",
            "relief": "flat",
            "cursor": "hand2",
            "padx": 10,
            "pady": 0,
        }
        tk.Button(group_frame, text="<", command=self._prev_paren, **arrow_style).pack(
            side="left", padx=4
        )
        self.group_label = tk.Label(
            group_frame,
            text="Grouping 1 / 5",
            bg=TABLE_BG,
            fg="#CCCCCC",
            font=("Arial", 12),
            width=14,
        )
        self.group_label.pack(side="left", padx=4)
        tk.Button(group_frame, text=">", command=self._next_paren, **arrow_style).pack(
            side="left", padx=4
        )

        # Expression preview
        self.expr_label = tk.Label(
            self.root, text="", bg=TABLE_BG, fg="#FFD700", font=("Courier", 16, "bold")
        )
        self.expr_label.pack(pady=(6, 2))

        # Result preview
        self.result_label = tk.Label(
            self.root, text="", bg=TABLE_BG, fg="#CCCCCC", font=("Arial", 13)
        )
        self.result_label.pack(pady=(0, 4))

        # Action buttons
        btn_frame = tk.Frame(self.root, bg=TABLE_BG)
        btn_frame.pack(pady=(4, 4))
        btn_style = {
            "font": ("Arial", 13, "bold"),
            "relief": "flat",
            "cursor": "hand2",
            "padx": 18,
            "pady": 6,
        }
        self.submit_btn = tk.Button(
            btn_frame,
            text="Submit",
            bg="#FFD700",
            fg="#1a1a1a",
            activebackground="#FFC300",
            command=self._submit,
            **btn_style,
        )
        self.submit_btn.pack(side="left", padx=5)
        self.skip_btn = tk.Button(
            btn_frame,
            text="Skip",
            bg="#555555",
            fg="#1a1a1a",
            activebackground="#777777",
            command=self._skip,
            **btn_style,
        )
        self.skip_btn.pack(side="left", padx=5)
        self.hint_btn = tk.Button(
            btn_frame,
            text="Hint (-1pt)",
            bg="#555555",
            fg="#1a1a1a",
            activebackground="#777777",
            command=self._hint,
            **btn_style,
        )
        self.hint_btn.pack(side="left", padx=5)

        # Feedback
        self.feedback_label = tk.Label(
            self.root, text="", bg=TABLE_BG, fg="white", font=("Arial", 13), wraplength=600
        )
        self.feedback_label.pack(pady=(0, 12))

    # ---- Drawing ----

    def _redraw(self) -> None:
        self.canvas.delete("all")

        # Draw cards
        for i, card in enumerate(self.hand):
            if i == self._drag_idx:
                x, y = slot_x(i), CARD_TOP
                draw_rounded_rect(
                    self.canvas,
                    x,
                    y,
                    x + CARD_W,
                    y + CARD_H,
                    r=CARD_RADIUS,
                    fill="#0e7a2e",
                    outline="#2a8d2a",
                    width=2,
                    dash=(4, 4),
                )
            else:
                draw_card_at(self.canvas, slot_x(i), CARD_TOP, card, tag=f"card{i}")

        # Draw operator circles
        for i in range(3):
            cx = op_center_x(i)
            cy = CARD_TOP + CARD_H // 2
            r = 22
            self.canvas.create_oval(
                cx - r,
                cy - r,
                cx + r,
                cy + r,
                fill="#2a5d2a",
                outline="#4a9d4a",
                width=2,
                tags=f"op{i}",
            )
            self.canvas.create_text(
                cx,
                cy,
                text=OPS[self.ops[i]],
                fill="white",
                font=("Arial", 20, "bold"),
                tags=f"op{i}",
            )

        # Draw bracket arcs
        self._draw_brackets()

        self._update_expression()

    def _draw_brackets(self) -> None:
        arcs = BRACKET_ARCS[self.paren_idx]
        for step, (left, right, level) in enumerate(arcs):
            color = BRACKET_COLORS[min(step, len(BRACKET_COLORS) - 1)]
            x1 = slot_center_x(left)
            x2 = slot_center_x(right)
            y_top = BRACKET_TOP + level * BRACKET_SPACING
            y_bot = y_top + BRACKET_SPACING - 6

            # Draw U-shaped bracket: left vertical, bottom horizontal, right vertical
            w = 2
            # Left leg
            self.canvas.create_line(x1, y_top, x1, y_bot, fill=color, width=w, tags="brackets")
            # Bottom bar
            self.canvas.create_line(x1, y_bot, x2, y_bot, fill=color, width=w, tags="brackets")
            # Right leg
            self.canvas.create_line(x2, y_top, x2, y_bot, fill=color, width=w, tags="brackets")

            # Step number in the middle of the bottom bar
            mid_x = (x1 + x2) // 2
            self.canvas.create_oval(
                mid_x - 9, y_bot - 9, mid_x + 9, y_bot + 9, fill=color, outline="", tags="brackets"
            )
            self.canvas.create_text(
                mid_x,
                y_bot,
                text=str(step + 1),
                fill="#1a1a1a",
                font=("Arial", 10, "bold"),
                anchor="center",
                tags="brackets",
            )

    def _update_expression(self) -> None:
        values = [str(c.value) for c in self.hand]
        ops = [OPS[i] for i in self.ops]
        fmt = PAREN_FMTS[self.paren_idx]
        expr = fmt(values, ops)
        self.expr_label.config(text=expr)

        result = evaluate_expression(expr)
        if result is not None:
            if abs(result - 24) < 1e-9:
                self.result_label.config(text="= 24 !", fg="#90EE90")
            else:
                self.result_label.config(text=f"= {result:.6g}", fg="#CCCCCC")
        else:
            self.result_label.config(text="= ??", fg="#FF9999")

        self.group_label.config(text=f"Grouping {self.paren_idx + 1} / 5")

    # ---- Grouping navigation ----

    def _prev_paren(self) -> None:
        self.paren_idx = (self.paren_idx - 1) % len(PAREN_FMTS)
        self._redraw()

    def _next_paren(self) -> None:
        self.paren_idx = (self.paren_idx + 1) % len(PAREN_FMTS)
        self._redraw()

    # ---- Operator cycling ----

    def _click_op(self, idx: int) -> None:
        self.ops[idx] = (self.ops[idx] + 1) % len(OPS)
        self._redraw()

    # ---- Drag and drop ----

    def _hit_card(self, mx: int, my: int) -> int | None:
        for i in range(4):
            x = slot_x(i)
            if x <= mx <= x + CARD_W and CARD_TOP <= my <= CARD_TOP + CARD_H:
                return i
        return None

    def _hit_op(self, mx: int, my: int) -> int | None:
        cy = CARD_TOP + CARD_H // 2
        for i in range(3):
            cx = op_center_x(i)
            if (mx - cx) ** 2 + (my - cy) ** 2 <= 22**2:
                return i
        return None

    def _on_press(self, event: tk.Event) -> None:
        op_idx = self._hit_op(event.x, event.y)
        if op_idx is not None:
            self._click_op(op_idx)
            return

        card_idx = self._hit_card(event.x, event.y)
        if card_idx is None:
            return
        self._drag_idx = card_idx
        self._drag_offset_x = event.x - slot_x(card_idx)
        self._drag_offset_y = event.y - CARD_TOP
        self._redraw()
        draw_card_at(
            self.canvas,
            event.x - self._drag_offset_x,
            event.y - self._drag_offset_y,
            self.hand[card_idx],
            tag="dragging",
            highlight=True,
        )

    def _on_drag(self, event: tk.Event) -> None:
        if self._drag_idx is None:
            return
        self.canvas.delete("dragging")
        draw_card_at(
            self.canvas,
            event.x - self._drag_offset_x,
            event.y - self._drag_offset_y,
            self.hand[self._drag_idx],
            tag="dragging",
            highlight=True,
        )

    def _on_release(self, event: tk.Event) -> None:
        if self._drag_idx is None:
            return
        drop_x = event.x - self._drag_offset_x + CARD_W // 2
        best_slot = self._drag_idx
        best_dist = float("inf")
        for i in range(4):
            center = slot_x(i) + CARD_W // 2
            dist = abs(drop_x - center)
            if dist < best_dist:
                best_dist = dist
                best_slot = i

        if best_slot != self._drag_idx:
            i, j = self._drag_idx, best_slot
            self.hand[i], self.hand[j] = self.hand[j], self.hand[i]

        self._drag_idx = None
        self.canvas.delete("dragging")
        self._redraw()

    # ---- Game logic ----

    def _new_game(self) -> None:
        self.deck = build_deck()
        self.score = 0
        self.rounds = 0
        self._next_round()

    def _update_info(self) -> None:
        self.score_label.config(text=f"Score: {self.score}")
        self.round_label.config(text=f"Round {self.rounds}")
        self.cards_left_label.config(text=f"Cards left: {len(self.deck)}")

    def _next_round(self) -> None:
        if len(self.deck) < 4:
            self._game_over()
            return

        self.hand = [self.deck.pop() for _ in range(4)]
        self.solution = can_make_24([c.value for c in self.hand])
        self.rounds += 1
        self.ops = [0, 0, 0]
        self.paren_idx = 0
        self._drag_idx = None

        self._update_info()
        self._redraw()

        if self.solution:
            self.status_label.config(
                text="Drag cards to reorder  |  Click operators to cycle  |  A solution exists!",
                fg="#90EE90",
            )
        else:
            self.status_label.config(
                text="Drag cards to reorder  |  Click operators to cycle  |  No solution possible",
                fg="#FF9999",
            )
        self.feedback_label.config(text="")

    def _get_expression(self) -> str:
        values = [str(c.value) for c in self.hand]
        ops = [OPS[i] for i in self.ops]
        return PAREN_FMTS[self.paren_idx](values, ops)

    def _submit(self) -> None:
        expr = self._get_expression()
        result = evaluate_expression(expr)
        if result is not None and abs(result - 24) < 1e-9:
            self.score += 1
            self.feedback_label.config(text=f"Correct! {expr} = 24  (+1 point)", fg="#90EE90")
            self._update_info()
            self._set_buttons_enabled(False)
            self.root.after(1200, self._resume_round)
        else:
            val = f"{result:.4g}" if result is not None else "??"
            self.feedback_label.config(text=f"{expr} = {val}, not 24. Keep trying!", fg="#FF9999")

    def _skip(self) -> None:
        if self.solution:
            self.score -= 1
            self.feedback_label.config(
                text=f"Solution was: {self.solution}  (-1 point)", fg="#FF9999"
            )
        else:
            self.feedback_label.config(text="Correct, no solution! No penalty.", fg="#90EE90")
        self._update_info()
        self._set_buttons_enabled(False)
        self.root.after(1500, self._resume_round)

    def _hint(self) -> None:
        if self.solution:
            self.score -= 1
            self.feedback_label.config(text=f"Hint: {self.solution}  (-1 point)", fg="#FFD700")
            self._update_info()
        else:
            self.feedback_label.config(text="No solution exists for these cards.", fg="#FFD700")

    def _set_buttons_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self.submit_btn.config(state=state)
        self.skip_btn.config(state=state)
        self.hint_btn.config(state=state)

    def _resume_round(self) -> None:
        self._set_buttons_enabled(True)
        self._next_round()

    def _game_over(self) -> None:
        self.canvas.delete("all")
        self.canvas.create_text(
            CANVAS_W // 2,
            CANVAS_H // 2,
            text="GAME OVER",
            fill="#FFD700",
            font=("Arial", 36, "bold"),
            anchor="center",
        )
        self.status_label.config(text="")
        self.expr_label.config(text="")
        self.result_label.config(text="")
        self.feedback_label.config(
            text=f"Final Score: {self.score} / {self.rounds} rounds", fg="white"
        )
        self._set_buttons_enabled(False)

        self.play_again_btn = tk.Button(
            self.root,
            text="Play Again",
            bg="#FFD700",
            fg="#1a1a1a",
            font=("Arial", 13, "bold"),
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=6,
            activebackground="#FFC300",
            command=self._restart,
        )
        self.play_again_btn.pack(pady=(0, 12))

    def _restart(self) -> None:
        self.play_again_btn.destroy()
        self._set_buttons_enabled(True)
        self._new_game()


def main() -> None:
    root = tk.Tk()
    Game(root)
    root.mainloop()


if __name__ == "__main__":
    main()

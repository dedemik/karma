"""Hesap makinesi: tema renkleriyle, çalışan bir hesap makinesi."""

from __future__ import annotations

from .base import App

KEYS = [
    ["C", "⌫", "%", "÷"],
    ["7", "8", "9", "×"],
    ["4", "5", "6", "−"],
    ["1", "2", "3", "+"],
    ["±", "0", ".", "="],
]

OPERATORS = {"÷": "/", "×": "*", "−": "-", "+": "+", "%": "/100"}


class CalcApp(App):
    id = "calc"
    title = "Hesap Makinesi"
    width = 380
    height = 540

    def build(self, parent) -> None:
        self.buffer = self.state.get("buffer", "0")

        screen = self.frame(parent, bg=self.wt["field"])
        screen.pack(fill="x", pady=(0, 12))

        self.expression = self.label(screen, "", muted=True, bg=self.wt["field"])
        self.expression.pack(anchor="e", padx=14, pady=(12, 0))

        self.display = self.label(screen, self.buffer, big=True, bg=self.wt["field"])
        self.display.configure(font=(self.fonts["huge"][0], 30, "bold"))
        self.display.pack(anchor="e", padx=14, pady=(0, 14))

        grid = self.frame(parent)
        grid.pack(fill="both", expand=True)
        for col in range(4):
            grid.columnconfigure(col, weight=1, uniform="key")
        for row in range(5):
            grid.rowconfigure(row, weight=1, uniform="key")

        for r, row in enumerate(KEYS):
            for c, key in enumerate(row):
                accent = key == "="
                button = self.button(
                    grid, key,
                    lambda k=key: self._press(k),
                    kind="accent" if accent else "normal",
                )
                button.configure(font=(self.fonts["bold"][0], 14, "bold"), pady=12)
                button.grid(row=r, column=c, sticky="nsew", padx=3, pady=3)

    # ---------------------------------------------------------------- mantık
    def _press(self, key: str) -> None:
        if key == "C":
            self.buffer = "0"
            self.expression.configure(text="")
        elif key == "⌫":
            self.buffer = self.buffer[:-1] or "0"
        elif key == "±":
            self.buffer = self.buffer[1:] if self.buffer.startswith("-") else "-" + self.buffer
        elif key == "=":
            self._evaluate()
            return
        elif key in OPERATORS:
            self.buffer += OPERATORS[key]
        else:
            self.buffer = (self.buffer + key) if self.buffer != "0" else key
        self._refresh()

    def _evaluate(self) -> None:
        expression = self.buffer.replace("÷", "/").replace("×", "*").replace("−", "-")
        try:
            result = eval(expression, {"__builtins__": None}, {})  # noqa: S307 - simülasyon
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            self.expression.configure(text=self.buffer + " =")
            self.buffer = str(result)
        except Exception:
            self.expression.configure(text="geçersiz ifade")
            self.buffer = "0"
        self._refresh()

    def _refresh(self) -> None:
        self.display.configure(text=self.buffer or "0")

    def get_state(self) -> dict:
        return {"buffer": self.buffer}

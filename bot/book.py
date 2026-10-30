"""Opening book loader for polyglot opening books."""

from __future__ import annotations

import os
from pathlib import Path

try:
    import chess
    import chess.polyglot
except ImportError:  # pragma: no cover - graceful fallback for missing optional dependency
    chess = None
    chess_polyglot = None


class OpeningBook:
    """Very small loader for a polyglot book if present."""

    def __init__(self, path: str | os.PathLike[str] | None = None) -> None:
        self.path = Path(path) if path is not None else Path("data/openings.bin")
        self._book = None

    def load(self):
        if chess is None:
            return None
        if not self.path.exists():
            return None
        try:
            with open(self.path, "rb") as fh:
                self._book = chess.polyglot.load(fh)
        except Exception:
            self._book = None
        return self._book

    def choose_move(self, board) -> object | None:
        if self._book is None:
            return None
        try:
            return self._book.get(board)
        except Exception:
            return None

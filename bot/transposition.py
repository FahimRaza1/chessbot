"""Simple transposition table for caching search results."""

from __future__ import annotations

from dataclasses import dataclass

import chess


@dataclass
class TTEntry:
    depth: int
    score: int
    best_move: chess.Move | None
    exact: bool = True


class TranspositionTable:
    def __init__(self) -> None:
        self.table: dict[str, TTEntry] = {}

    def key(self, board: chess.Board) -> str:
        return board.fen()

    def lookup(self, board: chess.Board, depth: int) -> TTEntry | None:
        entry = self.table.get(self.key(board))
        if entry is None or entry.depth < depth or not entry.exact:
            return None
        return entry

    def store(self, board: chess.Board, depth: int, score: int, best_move: chess.Move | None, exact: bool = True) -> None:
        self.table[self.key(board)] = TTEntry(depth=depth, score=score, best_move=best_move, exact=exact)

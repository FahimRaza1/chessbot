"""Move ordering heuristics for alpha-beta search."""

from __future__ import annotations

import chess


def order_moves(board: chess.Board, moves: list[chess.Move]) -> list[chess.Move]:
    """Return legal moves sorted by priority: captures, checks, promotions."""
    def score(move: chess.Move) -> int:
        score_value = 0
        captured = board.piece_at(move.to_square)
        if captured is not None:
            score_value += 10 * (captured.piece_type if captured.color != board.turn else 0)
        if board.is_capture(move):
            score_value += 1000
        if board.gives_check(move):
            score_value += 200
        if move.promotion is not None:
            score_value += 900
        return score_value

    return sorted(moves, key=score, reverse=True)

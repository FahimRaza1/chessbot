"""Alpha-beta chess search with quiescence and iterative deepening."""

from __future__ import annotations

import chess

from bot.evaluate import evaluate
from bot.ordering import order_moves
from bot.transposition import TranspositionTable

INF = 10**9
MATE_SCORE = 100000


def quiescence(board: chess.Board, alpha: int, beta: int, max_depth: int = 0) -> int:
    """Search forcing captures and checks beyond the normal horizon."""
    if board.is_checkmate():
        return -MATE_SCORE + 1

    if board.is_check():
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return -MATE_SCORE + 1
        if max_depth <= 0:
            score = evaluate(board)
            return score if board.turn == chess.WHITE else -score
        tactical_moves = list(board.legal_moves)
    else:
        score = evaluate(board)
        stand_pat = score if board.turn == chess.WHITE else -score
        if stand_pat >= beta:
            return beta
        if stand_pat > alpha:
            alpha = stand_pat
        if max_depth <= 0:
            return alpha
        tactical_moves = [move for move in board.legal_moves if board.is_capture(move) or board.gives_check(move)]

    tactical_moves = order_moves(board, tactical_moves)
    for move in tactical_moves:
        board.push(move)
        score = -quiescence(board, -beta, -alpha, max_depth - 1)
        board.pop()
        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    return alpha


def negamax(board: chess.Board, depth: int, alpha: int, beta: int, tt: TranspositionTable | None = None) -> int:
    """Alpha-beta negamax search."""
    if board.is_checkmate():
        return -MATE_SCORE
    if board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves() or board.is_fivefold_repetition():
        return 0
    if depth == 0:
        return quiescence(board, alpha, beta, max_depth=4)

    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return 0

    if tt is not None:
        entry = tt.lookup(board, depth)
        if entry is not None:
            return entry.score

    best_score = -INF
    ordered_moves = order_moves(board, legal_moves)
    best_move = None
    cutoff = False

    for move in ordered_moves:
        board.push(move)
        score = -negamax(board, depth - 1, -beta, -alpha, tt)
        board.pop()

        if score > best_score:
            best_score = score
            best_move = move
        if score > alpha:
            alpha = score
        if alpha >= beta:
            cutoff = True
            break

    if tt is not None:
        tt.store(board, depth, best_score, best_move, exact=not cutoff)

    return best_score


def search_best_move(board: chess.Board, depth: int = 2) -> chess.Move | None:
    """Return the best move after iterative deepening up to ``depth``."""
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None

    tt = TranspositionTable()
    best_move = legal_moves[0]
    for current_depth in range(1, max(1, depth) + 1):
        iteration_move = None
        best_score = -INF
        alpha = -INF
        beta = INF

        for move in order_moves(board, legal_moves):
            board.push(move)
            score = -negamax(board, current_depth - 1, -beta, -alpha, tt)
            board.pop()
            if score > best_score:
                best_score = score
                iteration_move = move
            alpha = max(alpha, score)

        if iteration_move is not None:
            best_move = iteration_move

    return best_move

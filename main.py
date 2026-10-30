"""Simple terminal chess game against the local engine."""

from __future__ import annotations

import chess

from bot.search import search_best_move


def play_game() -> None:
    board = chess.Board()
    print("Chess bot terminal match")
    print("Moves are entered in standard UCI format, e.g. e2e4")

    while not board.is_game_over():
        print(board)
        if board.turn == chess.WHITE:
            move = input("Your move: ").strip()
            if not move:
                continue
            try:
                move_obj = chess.Move.from_uci(move)
            except ValueError:
                print("Invalid move. Try again.")
                continue
            if move_obj not in board.legal_moves:
                print("Illegal move. Try again.")
                continue
            board.push(move_obj)
        else:
            move_obj = search_best_move(board, depth=2)
            if move_obj is None:
                break
            print(f"Bot plays: {move_obj.uci()}")
            board.push(move_obj)

    print(board)
    if board.is_checkmate():
        result = "checkmate"
        if board.turn == chess.WHITE:
            print("Black wins by checkmate.")
        else:
            print("White wins by checkmate.")
    elif board.is_stalemate():
        print("Draw by stalemate.")
    else:
        print("Game over.")


if __name__ == "__main__":
    play_game()

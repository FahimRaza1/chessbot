"""Minimal UCI wrapper for lichess-bot."""

from __future__ import annotations

import sys

import chess

from bot.search import search_best_move


def main() -> None:
    board = chess.Board()
    while True:
        command = sys.stdin.readline()
        if not command:
            break
        command = command.strip()
        if not command:
            continue

        if command == "uci":
            print("id name ChessBot")
            print("id author Copilot")
            print("uciok")
        elif command == "isready":
            print("readyok")
        elif command == "ucinewgame":
            board = chess.Board()
        elif command.startswith("position"):
            if command == "position startpos":
                board = chess.Board()
            elif command.startswith("position fen "):
                fen = command[len("position fen "):]
                board = chess.Board(fen)
            elif command.startswith("position startpos moves"):
                board = chess.Board()
                moves = command[len("position startpos moves "):].split()
                for move in moves:
                    try:
                        board.push_uci(move)
                    except ValueError:
                        pass
        elif command.startswith("go"):
            move = search_best_move(board, depth=2)
            if move is not None:
                print(f"bestmove {move.uci()}")
            else:
                print("bestmove 0000")
        elif command == "quit":
            break


if __name__ == "__main__":
    main()

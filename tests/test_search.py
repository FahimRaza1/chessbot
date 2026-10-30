import chess

from bot.search import search_best_move


def test_finds_mate_in_one():
    board = chess.Board("7k/5Q2/6K1/8/8/8/8/8 w - - 0 1")
    move = search_best_move(board, depth=2)
    assert move is not None
    board.push(move)
    assert board.is_checkmate()


def test_search_does_not_crash_on_empty_position():
    board = chess.Board.empty()
    assert search_best_move(board, depth=1) is None

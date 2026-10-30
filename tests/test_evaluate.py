import chess

from bot.evaluate import evaluate


def test_evaluate_starting_position_is_zero():
    board = chess.Board()
    assert evaluate(board) == 0


def test_evaluate_equal_material_is_neutral():
    board = chess.Board.empty()
    board.set_piece_at(chess.E4, chess.Piece(chess.PAWN, chess.WHITE))
    board.set_piece_at(chess.E5, chess.Piece(chess.PAWN, chess.BLACK))
    assert evaluate(board) == 0


def test_evaluate_prefers_material_advantage():
    board = chess.Board.empty()
    board.set_piece_at(chess.E4, chess.Piece(chess.PAWN, chess.WHITE))
    assert evaluate(board) > 0

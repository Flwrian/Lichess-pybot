from __future__ import annotations
import chess
from chess.engine import PlayResult
import random
from engine_wrapper import MinimalEngine
from typing import Any
import time

class FlowBot(MinimalEngine):

    depth = 5

    piece_square_tables = {
            chess.PAWN: [
                0, 0, 0, 0, 0, 0, 0, 0,
                50, 50, 50, 50, 50, 50, 50, 50,
                10, 10, 20, 30, 30, 20, 10, 10,
                5, 5, 10, 25, 25, 10, 5, 5,
                0, 0, 0, 20, 20, 0, 0, 0,
                5, -5, -10, 0, 0, -10, -5, 5,
                5, 10, 10, -20, -20, 10, 10, 5,
                0, 0, 0, 0, 0, 0, 0, 0
            ],
            chess.KNIGHT: [
                -50, -40, -30, -30, -30, -30, -40, -50,
                -40, -20, 0, 0, 0, 0, -20, -40,
                -30, 0, 10, 15, 15, 10, 0, -30,
                -30, 5, 15, 20, 20, 15, 5, -30,
                -30, 0, 15, 20, 20, 15, 0, -30,
                -30, 5, 10, 15, 15, 10, 5, -30,
                -40, -20, 0, 5, 5, 0, -20, -40,
                -50, -40, -30, -30, -30, -30, -40, -50
            ],
            chess.BISHOP: [
                -20, -10, -10, -10, -10, -10, -10, -20,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -10, 0, 5, 10, 10, 5, 0, -10,
                -10, 5, 5, 10, 10, 5, 5, -10,
                -10, 0, 10, 10, 10, 10, 0, -10,
                -10, 10, 10, 10, 10, 10, 10, -10,
                -10, 5, 0, 0, 0, 0, 5, -10,
                -20, -10, -10, -10, -10, -10, -10, -20
            ],
            chess.ROOK: [
                0, 0, 0, 0, 0, 0, 0, 0,
                5, 10, 10, 10, 10, 10, 10, 5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                -5, 0, 0, 0, 0, 0, 0, -5,
                0, 0, 0, 5, 5, 0, 0, 0
            ],
            chess.QUEEN: [
                -20, -10, -10, -5, -5, -10, -10, -20,
                -10, 0, 0, 0, 0, 0, 0, -10,
                -10, 0, 5, 5, 5, 5, 0, -10,
                -5, 0, 5, 5, 5, 5, 0, -5,
                0, 0, 5, 5, 5, 5, 0, -5,
                -10, 5, 5, 5, 5, 5, 0, -10,
                -10, 0, 5, 0, 0, 0, 0, -10,
                -20, -10, -10, -5, -5, -10, -10, -20
            ],
            chess.KING: [
                20, 30, 10, 0, 0, 10, 30, 20,
                20, 20, 0, 0, 0, 0, 20, 20,
                -10, -20, -20, -20, -20, -20, -20, -10,
                -20, -30, -30, -40, -40, -30, -30, -20,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30,
                -30, -40, -40, -50, -50, -40, -40, -30
            ]
        }

    material_score = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }

    transposition_table = {}

    def alpha_beta_search(self, board: chess.Board, depth: int, alpha: int, beta: int) -> int:
        key = board.fen() + str(depth) + str(alpha) + str(beta)
        if key in self.transposition_table:
            return self.transposition_table[key]
        if depth == 0:
            return self.evaluate(board)
        for move in board.legal_moves:
            board.push(move)
            score = -self.alpha_beta_search(board, depth - 1, -beta, -alpha)
            board.pop()
            if score >= beta:
                self.transposition_table[key] = score
                return score
            if score > alpha:
                alpha = score
        self.transposition_table[key] = alpha
        return alpha

    def alpha_beta(self, board: chess.Board, depth: int) -> int:
        best_score = -9999
        best_move = None
        for move in board.legal_moves:
            board.push(move)
            score = -self.alpha_beta_search(board, depth - 1, -9999, 9999)
            board.pop()
            if score > best_score:
                best_score = score
                best_move = move
        return best_move, best_score

    def evaluate(self, board: chess.Board) -> int:

        score = 0

        # Evaluate material score
        for piece_type in chess.PIECE_TYPES:
            score += len(board.pieces(piece_type, chess.WHITE)) * self.material_score[piece_type]
            score -= len(board.pieces(piece_type, chess.BLACK)) * self.material_score[piece_type]

        # Evaluate piece square tables
        for piece_type in chess.PIECE_TYPES:
            for square in chess.SquareSet(board.pieces(piece_type, chess.WHITE)):
                score += self.piece_square_tables[piece_type][square]

            for square in chess.SquareSet(board.pieces(piece_type, chess.BLACK)):
                score -= self.piece_square_tables[piece_type][chess.square_mirror(square)]

        # Evaluate check
        if board.is_check():
            if board.turn == chess.WHITE:
                score -= 50
            else:
                score += 50

        # Evaluate checkmate
        if board.is_checkmate():
            if board.turn == chess.WHITE:
                score = -9999
            else:
                score = 9999

        # Evaluate stalemate
        if board.is_stalemate():
            score = 0

        return score

        

    def search(self, board: chess.Board, *args: Any) -> PlayResult:
        # If it's the first move, play the opening: e4 and Nc3 in any case
        if board.fullmove_number == 1:
            return PlayResult(board.parse_san("e4"), 0)

        if board.fullmove_number == 2:
            return PlayResult(board.parse_san("Nc3"), 0)

        print("Searching")

        # Initialize the stockfish engine
        engine = chess.engine.SimpleEngine.popen_uci("./stockfish2/stockfish2.exe")
        
        result = self.alpha_beta(board, self.depth)
        move = result[0]
        eval = result[1]

        if eval == 9999:
            print("Checkmate found")

        if eval == -9999:
            print("I'm in trouble")
            # Play random move
            move = random.choice(list(board.legal_moves))
        
        # Compare eval to stockfish eval (same depth) of move
        stockfish_eval = engine.analyse(board, chess.engine.Limit(depth=self.depth))["score"].white().score()

        print("-----------------------------")
        print("Eval:")
        print("FlowBot Eval: " + str(eval))
        print("Stockfish eval same depth: " + str(stockfish_eval))
        print("-----------------------------")
        
        
        return PlayResult(move, None)
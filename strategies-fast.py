from __future__ import annotations
import chess
from chess.engine import PlayResult
import random
from engine_wrapper import MinimalEngine
from typing import Any
import time
import hashlib

import pickle

class FlowBot(MinimalEngine):

    def save_table(self, table, filename):
        with open(filename, 'wb') as f:
            pickle.dump(table, f)

    def load_table(self, filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)

    depth = 4

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

    # transposition_table = load_table("transposition_table.pkl")

    # if transposition_table is None:
    #     transposition_table = {}

    transposition_table = {}
    evaluated_positions = 0


    def alpha_beta_search(self, board: chess.Board, depth: int, alpha: int, beta: int, player_color: chess.Color) -> int:
        self.evaluated_positions += 1
        if depth == 0:
            return self.evaluate(board, player_color)
        for move in board.legal_moves:
            board.push(move)
            score = -self.alpha_beta_search(board, depth - 1, -beta, -alpha, player_color)
            board.pop()
            if score >= beta:
                return score
            if score > alpha:
                alpha = score
        return alpha

    def alpha_beta(self, board: chess.Board, depth: int, player_color: chess.Color) -> int:
        best_score = -9999
        best_move = None
        for move in board.legal_moves:
            board.push(move)
            score = -self.alpha_beta_search(board, depth - 1, -9999, 9999, player_color)
            board.pop()
            if score >= 9998:
                return move, score
            if score > best_score:
                best_score = score
                best_move = move

        return best_move, best_score


    def evaluate(self, board: chess.Board, player_color: chess.Color) -> int:

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

        if player_color == chess.BLACK:
            score = -score

        

    def search(self, board: chess.Board, *args: Any) -> PlayResult:
        # If it's the first move, play the opening: e4 and Nc3 in any case
        # if board.fullmove_number == 1 and board.turn == chess.WHITE:
        #     print("Playing opening")
        #     return PlayResult(board.parse_san("e4"), 0)

        # if board.fullmove_number == 2 and board.turn == chess.WHITE:
        #     return PlayResult(board.parse_san("Nc3"), 0)

        print("Searching")

        # Get the color of the player
        color = board.turn

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
        print("Evaluated positions: " + str(self.evaluated_positions))
        print("Eval:")
        print("FlowBot Eval: " + str(eval))
        print("Stockfish eval same depth: " + str(stockfish_eval))
        print("-----------------------------")
        
        
        return PlayResult(move, None)
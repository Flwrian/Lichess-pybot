from __future__ import annotations
import chess
from chess.engine import PlayResult
import random
from engine_wrapper import MinimalEngine
from typing import Any

class FlowBot(MinimalEngine):

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

    # Piece square tables for endgame (bonus for having pieces specially pawns and king on the other side of the board)
    piece_square_tables_endgame = {
            chess.PAWN: [
                0, 0, 0, 0, 0, 0, 0, 0,
                100, 100, 100, 100, 100, 100, 100, 100,
                80, 80, 80, 80, 80, 80, 80, 80,
                60, 60, 60, 60, 60, 60, 60, 60,
                40, 40, 40, 40, 40, 40, 40, 40,
                20, 20, 20, 20, 20, 20, 20, 20,
                10, 10, 10, 10, 10, 10, 10, 10,
                0, 0, 0, 0, 0, 0, 0, 0
            ],

            # Penalty for having the king in the back rank
            chess.KING: [
                0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0,
                -10, -10, -10, -10, -10, -10, -10, -10
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
    line = []


    def alpha_beta_search(self, board: chess.Board, depth: int, alpha: int, beta: int, player_color: chess.Color) -> int:

        self.evaluated_positions += 1
        if depth == 0:
            return self.evaluate(board, player_color)

        # Sort move by capture, then by piece value
        legal_moves = sorted(board.legal_moves, key=lambda move: (not board.is_capture(move), board.piece_type_at(move.from_square)), reverse=True)

        for move in legal_moves:
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
            if score > best_score:
                best_score = score
                best_move = move
            if best_score == 9999:
                break
                    

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

        return score
        

    def search(self, board: chess.Board, *args: Any) -> PlayResult:
        # If it's the first move, play the opening: e4 and Nc3 in any case
        # if board.fullmove_number == 1 and board.turn == chess.WHITE:
        #     print("Playing opening")
        #     return PlayResult(board.parse_san("e4"), 0)

        # if board.fullmove_number == 2 and board.turn == chess.WHITE:
        #     return PlayResult(board.parse_san("Nc3"), 0)

        color = board.turn
        self.evaluated_positions = 0
        # self.change_piece_square_by_material(board)

        # Initialize the stockfish engine
        engine = chess.engine.SimpleEngine.popen_uci("./stockfish2/stockfish2.exe")
        
        result = self.alpha_beta(board, self.depth, color)
        move = result[0]
        eval = result[1]

        if eval == 9999:
            print("Checkmate found")

        if eval == -9999:
            print("I'm in trouble")
            # Play random move
            move = random.choice(list(board.legal_moves))
        
        # Compare eval to stockfish eval (same depth) of move
        stockfish_eval = engine.analyse(board, chess.engine.Limit(depth=10))["score"].white().score()

        print("-----------------------------")
        print("Evaluated positions: " + str(self.evaluated_positions))
        print("Eval:")
        print("FlowBot Eval: " + str(eval))
        print("Stockfish eval same depth: " + str(stockfish_eval))
        print("-----------------------------")
        
        
        return PlayResult(move, None)
    
class FlowBot2(MinimalEngine):

    depth = 4

    material_score = {
        chess.PAWN: 100,
        chess.KNIGHT: 380,
        chess.BISHOP: 390,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }

    piece_square_tables = {
            chess.PAWN: [
                100, 100, 100, 100, 100, 100, 100, 100,
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

        return score

    def play(self, board: chess.Board):
        """
        The main function that gets called by the engine wrapper to make a move.
        """
        # Start by generating all possible legal moves for the current position
        legal_moves = list(board.legal_moves)

        # If there's only one legal move, we don't need to search any further
        if len(legal_moves) == 1:
            return PlayResult(move=legal_moves[0])

        # We'll use a simple minimax algorithm to find the best move
        best_score = float('-inf')
        best_move = None
        for move in legal_moves:
            board.push(move)
            score = self.minimax(board, depth=self.depth, alpha=float('-inf'), beta=float('inf'), maximizing_player=False)
            board.pop()
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def minimax(self, board: chess.Board, depth: int, alpha: float, beta: float, maximizing_player: bool) -> float:
        """
        The minimax algorithm with alpha-beta pruning.
        """
        if depth == 0 or board.is_game_over():
            return self.evaluate(board, board.turn)

        if maximizing_player:
            max_score = float('-inf')
            for move in board.legal_moves:
                board.push(move)
                max_score = max(max_score, self.minimax(board, depth=depth-1, alpha=alpha, beta=beta, maximizing_player=False))
                board.pop()
                alpha = max(alpha, max_score)
                if beta <= alpha:
                    break
            return max_score

        else:
            min_score = float('inf')
            for move in board.legal_moves:
                board.push(move)
                min_score = min(min_score, self.minimax(board, depth=depth-1, alpha=alpha, beta=beta, maximizing_player=True))
                board.pop()
                beta = min(beta, min_score)
                if beta <= alpha:
                    break
            return min_score
        
    def search(self, board: chess.Board, *args: Any) -> PlayResult:
        print("Searching")

        # Initialize the stockfish engine
        engine = chess.engine.SimpleEngine.popen_uci("./stockfish2/stockfish2.exe")
        
        result = self.play(board)
        
        
        return PlayResult(result, None)
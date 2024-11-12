import random

valueOfPiece = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "P": 1}
CHECKMATE = 1000
STALEMATE = 0
# negative value means black is winning, positive if white is winning

"""
Picks a random move
"""


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


"""
Greedy and Min/Max Algorithm (based on materials alone)
"""


def findGreedyMove(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1  # This makes algo works for both white and black
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentsMoves = gs.getValidMoves()
        opponentMaxScore = -CHECKMATE
        for oppsMove in opponentsMoves:
            gs.makeMove(oppsMove)
            if gs.checkmate:
                score = -turnMultiplier * CHECKMATE
            elif gs.stalemate:
                score = STALEMATE
            else:
                score = -turnMultiplier * scoreMaterial(gs.board)
            if score > opponentMaxScore:
                opponentMaxScore = score
            gs.undoMove()
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove


"""
Score board based on material.
"""


def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            piece = square[1]
            if square[0] == 'w':
                score += valueOfPiece[piece]
            elif square[0] == 'b':
                score -= valueOfPiece[piece]
    return score

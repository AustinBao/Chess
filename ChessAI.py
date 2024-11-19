import random

valueOfPiece = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "P": 1}

knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

bishopScores = [[4, 3, 2, 1, 1, 2, 3, 4],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 2, 2, 4, 3, 2],
                [1, 3, 3, 4, 4, 3, 3, 1],
                [1, 3, 3, 4, 4, 3, 3, 1],
                [2, 3, 4, 2, 2, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]]

queenScores = [[1, 1, 1, 3, 1, 1, 1, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 4, 3, 3, 3, 3, 4, 1],
               [1, 3, 2, 3, 3, 2, 3, 1],
               [1, 3, 2, 3, 3, 2, 3, 1],
               [1, 4, 3, 3, 3, 3, 4, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 1, 1, 3, 1, 1, 1, 1]]

rookScores = [[4, 2, 3, 4, 3, 4, 2, 4],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [1, 1, 2, 3, 3, 2, 1, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 1, 2, 3, 3, 2, 1, 1],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [4, 3, 4, 4, 4, 4, 3, 4]]

whitePawnScores = [[9, 9, 9, 9, 9, 9, 9, 9],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [5, 6, 7, 7, 7, 7, 6, 5],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnScores = [[0, 0, 0, 0, 0, 0, 0, 0],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [5, 6, 7, 7, 7, 7, 6, 5],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [9, 9, 9, 9, 9, 9, 9, 9]]

kingScores = [[2, 2, 5, 1, 1, 2, 5, 2],
             [1, 1, 1, 1, 1, 1, 1, 1],
             [1, 1, 1, 1, 1, 1, 1, 1],
             [1, 1, 1, 1, 1, 1, 1, 1],
             [1, 1, 1, 1, 1, 1, 1, 1],
             [1, 1, 1, 1, 1, 1, 1, 1],
             [1, 1, 1, 1, 1, 1, 1, 1],
             [2, 2, 5, 1, 1, 2, 5, 2]]

piecePositionScores = {"N": knightScores, "R": rookScores, "Q": queenScores, "K": kingScores, "B":bishopScores, "bP":blackPawnScores, "wP":whitePawnScores}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2
# negative value means black is winning, positive if white is winning

"""
Picks a random move
"""


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


"""
Greedy and then Min/Max Algorithm without recursion (based on materials alone)
"""


def findGreedyMove(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1  # This makes algo works for both white and black
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentsMoves = gs.getValidMoves()
        if gs.stalemate:
            opponentMaxScore = STALEMATE
        elif gs.checkmate:
            opponentMaxScore = -CHECKMATE
        else:
            opponentMaxScore = -CHECKMATE
            for oppsMove in opponentsMoves:
                gs.makeMove(oppsMove)
                gs.getValidMoves()
                if gs.checkmate:
                    score = CHECKMATE
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
Helper method to make the first recursive call in Min/Max algorithm
"""


def findBestMove(gs, validMoves, returnQueue):
    global nextMove, counter
    nextMove = None
    counter = 0
    # findMoveMinMax(gs, validMoves, DEPTH,gs.whiteToMove)
    # findMoveNegaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    print(counter)
    returnQueue.put(nextMove)


"""
Recursive Min/Max Algorithm
"""


def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove, counter
    counter += 1

    if depth == 0:
        return scoreMaterial(gs.board)

    random.shuffle(validMoves)
    if whiteToMove:
        maxScore = -CHECKMATE  # start at lowest score possible in order to find improvements
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore
    else:
        minScore = CHECKMATE  # start at highest score possible in order to find downgrades
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore


"""
Nega Max Algorithm (improved version of min/max algorithm)
"""


def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove, counter
    counter += 1

    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    maxScore = -CHECKMATE  # start at lowest score possible in order to find improvements
    random.shuffle(validMoves)
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax(gs, nextMoves, depth - 1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore


def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    """
    basically stops looking further down the recursion tree if a move you MADE is already terrible
    """
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    # move ordering - add later
    maxScore = -CHECKMATE  # start at lowest score possible in order to find improvements
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha:  # pruning happens
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


"""
More comprehensive evaluation of the board ("+" score is good for white)
"""


def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE  # Black wins
        else:
            return CHECKMATE  # White wins
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board)):
            square = gs.board[row][col]
            piece = square[1]
            if square != "--":
                # score it positionally
                if piece == "P":  # for pawns
                    piecePositionScore = piecePositionScores[square][row][col]
                else:  # for other pieces
                    piecePositionScore = piecePositionScores[piece][row][col]

                if square[0] == 'w':
                    score += valueOfPiece[piece] + piecePositionScore * 0.10
                elif square[0] == 'b':
                    score -= valueOfPiece[piece] + piecePositionScore * 0.10
    return score


"""
Score board ONLY based on material.
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

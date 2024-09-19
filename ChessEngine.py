# Stores all the information about the state of a chess game. Also determines valid moves + move log

class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, start, end, board):
        self.startRow = start[0]
        self.startCol = start[1]
        self.endRow = end[0]
        self.endCol = end[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    # Overriding equals method (this allows python to equate two different objects with the same value as equal)
    def __eq__(self, other):
        # other represents another Move object which we want to see is equal
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self) -> str:
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c) -> str:
        return self.colsToFiles[c] + self.rowsToRanks[r]


class GameState():
    def __init__(self):
        # 8x8 two-dimensional list. each element in the list has 2 characters.
        # the first is the color, the second is the type of piece.
        # "--" represents empty space
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunction = {"P": self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves,
                             "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []

    def makeMove(self, move: Move) -> None:
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

    def undoMove(self) -> None:
        if len(self.moveLog) != 0:
            lastMove = self.moveLog.pop()
            self.board[lastMove.startRow][lastMove.startCol] = lastMove.pieceMoved
            self.board[lastMove.endRow][lastMove.endCol] = lastMove.pieceCaptured
            self.whiteToMove = not self.whiteToMove

    # With checks in mind
    def getValidMoves(self):
        return self.getAllPossibleMoves()

    # looking at all moves
    def getAllPossibleMoves(self) -> list[Move]:
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]  # w or b
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunction[piece](r, c, moves)  # calls respective function to the piece inputted
        return moves

    def getPawnMoves(self, r, c, moves) -> None:
        if self.whiteToMove:
            if self.board[r - 1][c] == "--":  # 1 square advance
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":  # 2 square advance. Inside other if statement since if
                    # you cant even move one square forward, you won't be able to with 2 squares forward.
                    moves.append(Move((r, c), (r - 2, c), self.board))
            # This if stops pawns from capturing pawns from one side of the board to the other... kinda cool idea ngl
            if c - 1 >= 0:  # captures to the left
                if self.board[r - 1][c - 1][0] == "b":  # enemy piece to capture on the left diagonal
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
            # DON'T use elif here since this will ignore any possible captures to the right of pawns
            if c + 1 <= 7:  # captures to the right
                if self.board[r - 1][c + 1][0] == "b":  # enemy piece to capture on the left diagonal
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
        else:  # black pawn moves
            pass

    def getRookMoves(self, r, c, moves):
        pass

    def getKnightMoves(self, r, c, moves):
        pass

    def getBishopMoves(self, r, c, moves):
        pass

    def getQueenMoves(self, r, c, moves):
        pass

    def getKingMoves(self, r, c, moves):
        pass

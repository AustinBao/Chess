# Stores all the information about the state of a chess game. Also determines valid moves + move log

class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, start, end, board, isEnpassantMove=False):
        self.startRow = start[0]
        self.startCol = start[1]
        self.endRow = end[0]
        self.endCol = end[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # pawn promotion
        self.isPawnPromo = (self.pieceMoved == "wP" and self.endRow == 0) or (
                    self.pieceMoved == "bP" and self.endRow == 7)
        # en passant
        self.isEnpassantMove = isEnpassantMove

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
            ["--", "bR", "--", "--", "wP", "--", "--", "wR"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunction = {"P": self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves,
                             "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck()
        self.checkMate = False
        self.staleMate = False

    def makeMove(self, move: Move) -> None:
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        if move.isPawnPromo:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

    def undoMove(self) -> None:
        if len(self.moveLog) != 0:
            lastMove = self.moveLog.pop()
            self.board[lastMove.startRow][lastMove.startCol] = lastMove.pieceMoved
            self.board[lastMove.endRow][lastMove.endCol] = lastMove.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if lastMove.pieceMoved == "wK":
                self.whiteKingLocation = (lastMove.startRow, lastMove.startCol)
            elif lastMove.pieceMoved == "bK":
                self.blackKingLocation = (lastMove.startRow, lastMove.startCol)

    # With checks in mind
    def getValidMoves(self):
        # 1. generate all moves
        moves = self.getAllPossibleMoves()
        # 2. for each move, make the move
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            # 3. generate oppMoves and see if they attack you king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                # 4. if they do attack you king, remove that invalid move
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:  # either stalemate or checkmate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        return moves

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c) -> bool:
        self.whiteToMove = not self.whiteToMove
        opponentMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in opponentMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

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
                if self.board[r - 1][c + 1][0] == "b":  # enemy piece to capture on the right diagonal
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
        else:  # black pawn moves
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c + 1 >= 0:
                if self.board[r + 1][c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))

    def getRookMoves(self, r, c, moves) -> None:
        direction = [(0, 1), (0, -1), (-1, 0), (1, 0)]
        opponent = "b" if self.whiteToMove else "w"
        friendly = "w" if self.whiteToMove else "b"
        for d in direction:
            dr, dc = d[0], d[1]
            for i in range(1, 8):
                new_r, new_c = r + dr * i, c + dc * i
                if 0 <= new_r < 8 and 0 <= new_c < 8:
                    if self.board[new_r][new_c][0] == opponent:
                        moves.append(Move((r, c), (new_r, new_c), self.board))
                        break
                    elif self.board[new_r][new_c][0] == friendly:
                        break
                    moves.append(Move((r, c), (new_r, new_c), self.board))
                else:
                    break

    def getBishopMoves(self, r, c, moves) -> None:
        direction = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        opponent = "b" if self.whiteToMove else "w"
        friendly = "w" if self.whiteToMove else "b"
        for d in direction:
            dr, dc = d[0], d[1]
            for i in range(1, 8):
                new_r, new_c = r + dr * i, c + dc * i
                if 0 <= new_r < 8 and 0 <= new_c < 8:
                    if self.board[new_r][new_c][0] == opponent:
                        moves.append(Move((r, c), (new_r, new_c), self.board))
                        break
                    elif self.board[new_r][new_c][0] == friendly:
                        break
                    moves.append(Move((r, c), (new_r, new_c), self.board))
                else:
                    break

    def getKnightMoves(self, r, c, moves) -> None:
        direction = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (2, -1), (2, 1), (1, -2), (1, 2)]
        opponent = "b" if self.whiteToMove else "w"
        friendly = "w" if self.whiteToMove else "b"
        for x, y in direction:
            if 0 <= r + x <= 7 and 0 <= c + y <= 7:
                if self.board[r + x][c + y][0] != friendly:
                    moves.append(Move((r, c), (r + x, c + y), self.board))

    def getQueenMoves(self, r, c, moves) -> None:
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        directions = [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1), (0, -1), (0, 1)]
        friendly = "w" if self.whiteToMove else "b"
        for x, y in directions:
            newRow, newCol = r + x, c + y
            if 0 <= newRow <= 7 and 0 <= newCol <= 7:
                if self.board[newRow][newCol][0] != friendly:
                    moves.append(Move((r, c), (newRow, newCol), self.board))

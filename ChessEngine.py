# Stores all the information about the state of a chess game. Also determines valid moves + move log

import copy


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, start, end, board, isEnpassantMove=False, isCastleMove=False):
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
        if self.isEnpassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"
        # castle move
        self.isCastleMove = isCastleMove
        self.isCapture = self.pieceCaptured != "--"
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

    # Overriding the str() function
    def __str__(self):
        # castle move
        if self.isCastleMove:
            return "0-0" if self.endCol == 6 else "0-0-0"
        endSquare = self.getRankFile(self.endRow, self.endCol)
        # pawn moves
        if self.pieceMoved[1] == "P":
            if self.isCapture:
                return self.colsToFiles[self.startCol] + "x" + endSquare
            else:
                return endSquare
            # pawn promotions

        # checks (add +)

        # checkmates (add #)

        # two of the same type of piece moving to a square. Nbd2 is both knights can move to d2 (b is the file)

        # piece moves
        moveString = self.pieceMoved[1]
        if self.isCapture:
            moveString += "x"
        return moveString + endSquare


class GameState:
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
        self.enpassantPossible = ()  # coordinate where the en passant capture is possible
        self.enpassantPossibleLog = [self.enpassantPossible]  # so if we move a diff piece, the en passent is saved
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

        self.moveFunction = {"P": self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves,
                             "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck()
        self.checkmate = False
        self.stalemate = False

    def makeMove(self, move: Move) -> None:
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # log move
        self.whiteToMove = not self.whiteToMove  # switch turns
        # update king's position
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        #  Pawn promo
        if move.isPawnPromo:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        #  update enpassantPossible
        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.endRow + move.startRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()
        # makes undoing the move easier
        self.enpassantPossibleLog.append(self.enpassantPossible)

        #  Enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"

        # updates castling rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))
        # castle moves
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # king side castle move
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]  # moves rook
                self.board[move.endRow][move.endCol + 1] = "--"  # removes old rook
            else:
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]  # moves rook
                self.board[move.endRow][move.endCol - 2] = "--"  # removes old rook

    def undoMove(self) -> None:
        if len(self.moveLog) != 0:
            lastMove = self.moveLog.pop()
            self.board[lastMove.startRow][lastMove.startCol] = lastMove.pieceMoved
            self.board[lastMove.endRow][lastMove.endCol] = lastMove.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # switch turns
            # update king's position
            if lastMove.pieceMoved == "wK":
                self.whiteKingLocation = (lastMove.startRow, lastMove.startCol)
            elif lastMove.pieceMoved == "bK":
                self.blackKingLocation = (lastMove.startRow, lastMove.startCol)

            # undo en passant move
            if lastMove.isEnpassantMove:
                self.board[lastMove.endRow][lastMove.endCol] = "--"
                self.board[lastMove.startRow][lastMove.endCol] = lastMove.pieceCaptured
            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]

            # undo castling rights
            self.castleRightsLog.pop()
            castle_rights = copy.deepcopy(self.castleRightsLog[-1])
            self.currentCastlingRight = castle_rights

            # undo castle move
            if lastMove.isCastleMove:
                if lastMove.endCol - lastMove.startCol == 2:  # king side
                    self.board[lastMove.endRow][lastMove.endCol + 1] = self.board[lastMove.endRow][
                        lastMove.endCol - 1]  # moves rook
                    self.board[lastMove.endRow][lastMove.endCol - 1] = "--"  # removes old rook
                else:
                    self.board[lastMove.endRow][lastMove.endCol - 2] = self.board[lastMove.endRow][
                        lastMove.endCol + 1]  # moves rook
                    self.board[lastMove.endRow][lastMove.endCol + 1] = "--"  # removes old rook

            self.checkmate = False
            self.stalemate = False

    def updateCastleRights(self, move):
        # Checks if king moved
        if move.pieceMoved == "wK":
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False

        # Checks if rook moved
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastlingRight.bks = False

        # Checks if rook taken
        if move.pieceCaptured == "wR":
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == "bR":
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False

    # With checks in mind
    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        # 1. generate all moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
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
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
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
                elif (r - 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))

            # DON'T use elif here since this will ignore any possible captures to the right of pawns
            if c + 1 <= 7:  # captures to the right
                if self.board[r - 1][c + 1][0] == "b":  # enemy piece to capture on the right diagonal
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))

        else:  # black pawn moves
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c + 1 >= 0:
                if self.board[r + 1][c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))

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

    """
    Generate all valid castle moves for the king at (r,c) and add them to the list of moves
    """

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return  # can't castle when in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (
                not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (
                not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        # no need to check if king exits the board since we know king hasn't moved yet or else castle option is False
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
            # don't have to check if 3rd squareUnderAttack since king doesn't pass through there
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))

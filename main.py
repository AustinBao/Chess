# Main driver file. handles user input and displaying current GameState Object

import asyncio
import ChessAI
import ChessEngine
from multiprocessing import Process, Queue, freeze_support
import pygame as p

BOARD_WIDTH = BOARD_HEIGHT = 512  # 400 also works
MOVE_LOG_PANEL_WIDTH = 280
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
p.font.init()
my_font = p.font.SysFont('Comic Sans MS', 30)
colors = [p.Color("white"), p.Color("gray")]


async def main():
    screen, clock, gs, validMoves, moveLogFont = initialize_game()
    sqSelected, playerClicks = (), []
    moveMade, animate, gameOver = False, False, False
    moveUndone = False
    playerOne = True  # if a Human is playing white, then true. If AI is playing, then false
    playerTwo = True  # Same as above but for black
    AIThinking = False
    moveFinderProcess = None

    running = True
    while running:
        isHumanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN and not gameOver:
                sqSelected, playerClicks, moveMade, animate = handle_mouse_click(sqSelected, playerClicks, gs,
                                                                                 validMoves, moveMade, animate,
                                                                                 isHumanTurn)
            elif e.type == p.KEYDOWN:
                gs, validMoves, sqSelected, playerClicks, moveMade, animate, gameOver, AIThinking, moveUndone = handle_key_press(
                    e, gs, validMoves, sqSelected, playerClicks, gameOver, AIThinking, moveFinderProcess, moveUndone)

        # AI move finder logic
        if not gameOver and not isHumanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                returnQueue = Queue()  # used to pass data between threads
                moveFinderProcess = Process(target=ChessAI.findBestMove, args=(gs, validMoves, returnQueue))
                moveFinderProcess.start()  # calls ChessAI.findBestMove(gs, validMoves, returnQueue)

            if not moveFinderProcess.is_alive():
                AIMove = returnQueue.get()
                if AIMove is None:
                    AIMove = ChessAI.findRandomMove(validMoves)
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                AIThinking = False

        if moveMade:
            if animate:
                animateMoves(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        drawGameState(screen, gs, validMoves, gs.moveLog, sqSelected, moveLogFont)

        if gs.checkmate or gs.stalemate:
            gameOver = True
            game_over_text(gs, screen)

        clock.tick(MAX_FPS)
        p.display.flip()
        await asyncio.sleep(0)


"""
Loads img of chess pieces
"""


def loadImages():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR", "bP", "wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR",
              "wP"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("img/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    #     we can now access an image by keying the dict


"""
Draws everything on the board
"""


def drawGameState(screen, gs, validMoves, moveLog, sqSelected, moveLogFont):
    drawBoard(screen)  # draw squares on the board
    highlightSquares(screen, gs, validMoves, moveLog, sqSelected)
    drawPieces(screen, gs.board)  # draw pieces on top of the board
    drawMoveLog(screen, gs, moveLogFont)


"""
Just draws the board
"""


def drawBoard(screen):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
Just draws the pieces
"""


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i // 2 + 1) + ". " + str(moveLog[i]) + " "
        if i + 1 < len(moveLog):  # makes sure black makes a move
            moveString += str(moveLog[i + 1]) + "   "
        moveTexts.append(moveString)
    padding = 5
    textY = padding
    lineSpacing = 2
    movePerRow = 3
    for i in range(0, len(moveTexts), movePerRow):
        text = ""
        for j in range(movePerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i + j]  # gets the first three moves in the same string/row
        textObject = font.render(text, True, p.Color("white"))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing


"""
Starts pygame 
"""


def initialize_game():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    loadImages()  # only does this once since it's taxing
    moveLogFont = p.font.SysFont("Arial", 14, False, False)
    return screen, clock, gs, validMoves, moveLogFont


"""
Handles mouse inputs (ie. selecting/de-selecting pieces) 
"""


def handle_mouse_click(sqSelected, playerClicks, gs, validMoves, moveMade, animate, isHumanTurn):
    location = p.mouse.get_pos()
    col, row = location[0] // SQ_SIZE, location[1] // SQ_SIZE
    if sqSelected == (row, col) or col >= 8:  # (player clicks same square twice) or (user clicked the mouse log)
        sqSelected = ()
        playerClicks = []
    else:
        sqSelected = (row, col)
        playerClicks.append(sqSelected)
    if len(playerClicks) == 2 and isHumanTurn:
        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
        for i in range(len(validMoves)):
            if move == validMoves[i]:
                gs.makeMove(validMoves[i])
                moveMade = True
                animate = True
                sqSelected = ()
                playerClicks = []
        if not moveMade:
            playerClicks = [sqSelected]

    return sqSelected, playerClicks, moveMade, animate


"""
Handles keyboard inputs 
"""


def handle_key_press(e, gs, validMoves, sqSelected, playerClicks, gameOver, AIThinking, moveFinderProcess, moveUndone):
    moveMade = False
    animate = False
    if e.key == p.K_LEFT:  # undo move
        gs.undoMove()
        moveMade = True
        animate = False
        gameOver = False
        if AIThinking:
            moveFinderProcess.terminate()
            AIThinking = False
        moveUndone = True
    elif e.key == p.K_r:  # reset board when r is pressed
        gs = ChessEngine.GameState()
        validMoves = gs.getValidMoves()
        sqSelected = ()
        playerClicks = []
        moveMade = False
        animate = False
        gameOver = False
        if AIThinking:
            moveFinderProcess.terminate()
            AIThinking = False
        moveUndone = True
    return gs, validMoves, sqSelected, playerClicks, moveMade, animate, gameOver, AIThinking, moveUndone


"""
Handles display logic for who won and stalemate
"""


def game_over_text(gs, screen):
    if gs.checkmate:
        winner = "Black" if gs.whiteToMove else "White"
        drawEndGameText(screen, f"{winner} wins by checkmate")
    elif gs.stalemate:
        drawEndGameText(screen, "Stalemate")


"""
Highlight square selected and its moves
"""


def highlightSquares(screen, gs, validMoves, moveLog, sqSelected):
    # highlights the last move played
    if len(moveLog) != 0:
        last_r, last_c = moveLog[-1].endRow, moveLog[-1].endCol
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('blue'))
        screen.blit(s, (last_c * SQ_SIZE, last_r * SQ_SIZE))

    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"):  # make sure sqSelected is a piece that can be moved
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # 0 transparent; 255 opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(p.Color('yellow'))  # highlight possible moves
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


"""
Animating piece moves and captures
"""


def animateMoves(move, screen, board, clock):
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    print(f"Animating move from ({move.startRow}, {move.startCol}) to ({move.endRow}, {move.endCol})")

    framesPerSquare = 5
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * (frame / frameCount), move.startCol + dC * (frame / frameCount))
        drawBoard(screen)
        drawPieces(screen, board)
        # erase piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == "b" else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)




"""
Displays text depending on who won or stalemate
"""


def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    textObject = font.render(text, 0, p.Color("Gray"))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObject.get_width() / 2,
                                                                BOARD_HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":
    freeze_support()  # Necessary on Windows to avoid RuntimeError
    asyncio.run(main())

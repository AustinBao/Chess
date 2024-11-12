# Main driver file. handles user input and displaying current GameState Object

import pygame as p
import ChessEngine, ChessAI

WIDTH = HEIGHT = 512  # 400 also works
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
p.font.init()
my_font = p.font.SysFont('Comic Sans MS', 30)
colors = [p.Color("white"), p.Color("gray")]


def loadImages():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR", "bP", "wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR",
              "wP"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    #     we can now access an image by keying the dict


def initialize_game():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    loadImages()  # only does this once since it's taxing
    return screen, clock, gs, validMoves


def handle_mouse_click(sqSelected, playerClicks, gs, validMoves, moveMade, animate):
    location = p.mouse.get_pos()
    col, row = location[0] // SQ_SIZE, location[1] // SQ_SIZE
    if sqSelected == (row, col):  # player clicks same square twice
        sqSelected = ()
        playerClicks = []
    else:
        sqSelected = (row, col)
        playerClicks.append(sqSelected)
    if len(playerClicks) == 2:
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


def handle_key_press(e, gs, validMoves, sqSelected, playerClicks, gameOver):
    moveMade = False
    animate = False
    if e.key == p.K_LEFT:  # undo move
        gs.undoMove()
        moveMade = True
        animate = False
    elif e.key == p.K_r:  # reset board when r is pressed
        gs = ChessEngine.GameState()
        validMoves = gs.getValidMoves()
        sqSelected = ()
        playerClicks = []
        gameOver = False
    return gs, validMoves, sqSelected, playerClicks, moveMade, animate, gameOver


def game_over_text(gs, screen):
    if gs.checkmate:
        winner = "Black" if gs.whiteToMove else "White"
        drawText(screen, f"{winner} wins by checkmate")
    elif gs.stalemate:
        drawText(screen, "Stalemate")


def main():
    screen, clock, gs, validMoves = initialize_game()
    sqSelected, playerClicks = (), []
    moveMade, animate, gameOver = False, False, False
    playerOne = True  # if a Human is playing white, then true. If ai is playing, then false
    playerTwo = False  # Same as above but for black
    running = True
    while running:
        isHumanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN and not gameOver and isHumanTurn:
                sqSelected, playerClicks, moveMade, animate = handle_mouse_click(sqSelected, playerClicks, gs,
                                                                                 validMoves, moveMade, animate)
            elif e.type == p.KEYDOWN:
                gs, validMoves, sqSelected, playerClicks, moveMade, animate, gameOver = handle_key_press(e, gs,
                                                                                                         validMoves,
                                                                                                         sqSelected,
                                                                                                         playerClicks,
                                                                                                         gameOver)

        # AI move finder logic
        if not gameOver and not isHumanTurn:
            AIMove = ChessAI.findGreedyMove(gs, validMoves)
            if AIMove is None:
                AIMove = ChessAI.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMoves(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, gs.moveLog, sqSelected)

        if gs.checkmate or gs.stalemate:
            gameOver = True
            game_over_text(gs, screen)

        clock.tick(MAX_FPS)
        p.display.flip()


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
Animating piece moves
"""


def animateMoves(move, screen, board, clock):
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
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
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawGameState(screen, gs, validMoves, moveLog, sqSelected):
    drawBoard(screen)  # draw squares on the board
    highlightSquares(screen, gs, validMoves, moveLog, sqSelected)
    drawPieces(screen, gs.board)  # draw pieces on top of the board


def drawBoard(screen):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color("Gray"))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2,
                                                    HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))


if __name__ == "__main__":
    main()

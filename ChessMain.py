# Main driver file. handles user input and displaying current GameState Object

import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512  # 400 also works
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}


def loadImages():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR", "bP", "wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR",
              "wP"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    #     we can now access an image by keying the dict


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    loadImages()  # only does this once since its very taxing
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs):
    drawBoard(screen)  # draw squares on the board
    # add in pieces highlighting or move suggestions
    drawPieces(screen, gs.board)  # draw pieces on top of the board


def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for c in range(DIMENSION):
        for r in range(DIMENSION):
            color = colors[(r + c) % 2]
            square = p.Rect(r * SQ_SIZE, c * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            p.draw.rect(screen, color, square)


def drawPieces(screen, board):
    pass


if __name__ == "__main__":
    main()

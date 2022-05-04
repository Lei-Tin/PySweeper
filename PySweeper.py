"""
PySweeper - A minesweeper clone written solely in Python
Created by Ray
"""

import pygame
import random
from typing import List, Tuple, Union

from settings import *


class InvalidBombCountException(Exception):
    """The exception that will be raised when we have too much bombs and too less tiles"""

    def __str__(self) -> str:
        """The string representation of this exception"""
        return 'Invalid Bomb Count Exception: Perhaps the number of bombs is larger ' \
               'than the total number of tiles?'


class Board(object):
    """This is the class object of a board

    A Board object contains a _board that has a tile at the ith row, jth column,
    represented by self._board[i][j]

    The self._flags attribute is used to store which tiles are flagged.
    The self._opens attribute is used to keep track of which tiles are open already

    In each tile, there can either be a:
    - 'B', that is a bomb
    - String of a integer number ranging from 1 to 8 that represents
    how many bombs surround this tile
    - None, which is an empty tile

    Representation Invariant:
    - self._rows * self._columns > self._bombs_count
    """
    _rows: int
    _columns: int
    _board: List[List[Union[str, None]]]
    _bombs_count: int
    _flags: List[List[bool]]

    def __init__(self, rows: int, columns: int, bombs: int) -> None:
        """Initializes a mine sweeper game board with the specified rows and columns
        Starts off with an empty board with no bombs generated and
        """
        self._rows = rows
        self._columns = columns
        self._bombs_count = bombs

        if self._bombs_count >= self._rows * self._columns:
            raise InvalidBombCountException

        # Initializes a board with nothing, and also a flag with nothing
        self._board = [[None for _ in range(self._columns)] for _ in range(self._rows)]
        self._flags = [[False for _ in range(self._columns)] for _ in range(self._rows)]
        self._opens = [[False for _ in range(self._columns)] for _ in range(self._rows)]

        # Generates bomb
        self.generate_bombs()

        # Update number
        self.update_number()

    def get_rows(self) -> int:
        """Returns the number of rows of this minesweeper board"""
        return self._rows

    def get_columns(self) -> int:
        """Returns the number of columns of this minesweeper board"""
        return self._columns

    def get_tile(self, row: int, col: int) -> str:
        """Returns the string representation of the given tile"""
        if self._board[row][col] is None:
            return 'N'
        else:
            return self._board[row][col]

    def get_flag(self, row: int, col: int) -> bool:
        """Returns the flag status of the given tile"""
        return self._flags[row][col]

    def get_open(self, row: int, col: int) -> bool:
        """Returns if the specified tile is open or not"""
        return self._opens[row][col]

    def generate_bombs(self) -> None:
        """Generates _bombs_count number of bombs in the current board
        """
        curr_bombs = 0

        while curr_bombs < self._bombs_count:
            # Because randint includes both end point, so we have to remove 1 from the
            # right endpoint
            bomb_y = random.randint(0, self._rows - 1)
            bomb_x = random.randint(0, self._columns - 1)

            if self._board[bomb_y][bomb_x] == 'B':
                # If we bump into a place that already contains a bomb
                continue
            else:
                # Plant a bomb in there
                self._board[bomb_y][bomb_x] = 'B'
                curr_bombs += 1

    def update_open(self, row: int, col: int) -> None:
        """Updates the tile so that it is open in self._opens"""
        self._opens[row][col] = True

    def update_flag(self, row: int, col: int) -> None:
        """Swaps the flag status of the given index"""
        self._flags[row][col] = not self._flags[row][col]

    def update_number(self) -> None:
        """Updates the current board to contain integer numbers that symbolize how many
        bombs are surrounding it"""

        for r in range(self._rows):
            for c in range(self._columns):
                if self._board[r][c] is None:
                    self._board[r][c] = str(self.num_ajacent_bombs(r, c))

    def num_ajacent_bombs(self, row: int, col: int) -> int:
        """Returns the number of adjacent bombs of the current tile"""
        count = 0
        for h in (-1, 0, 1):
            for v in (-1, 0, 1):
                try:
                    if row + v < 0 or col + h < 0:
                        raise IndexError

                    if self._board[row + v][col + h] == 'B':
                        count += 1
                except IndexError:
                    pass

        return count

    def __str__(self) -> str:
        """Returns the string representation of the current board state
        Containing a row and column index on the side

        Legend:
        - N is None, empty tile
        - B is a bomb
        - Integer number is how much bombs we have surrounding the tile
        """
        s = '\t'

        for c in range(self._columns):
            s += f'{c}\t'

        s += '\n'

        for r in range(self._rows):
            for c in range(self._columns):
                char = 'N' if self._board[r][c] is None else self._board[r][c]

                if c == 0:
                    import string

                    s += f'{string.ascii_uppercase[r % 26] * (1 + r // 26)}\t{char}\t'
                elif c == self._columns - 1:
                    s += f'{char}\n'
                else:
                    s += f'{char}\t'

        return s


def initialize_screen() -> pygame.Surface:
    """Initialize pygame and the display window.
    """
    pygame.display.init()
    pygame.font.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)

    # White window size background
    screen.fill(pygame.colordict.THECOLORS['white'])
    pygame.display.flip()

    pygame.event.clear()
    pygame.event.set_blocked(None)
    pygame.event.set_allowed([pygame.QUIT] + [pygame.MOUSEBUTTONDOWN])

    return screen


def draw_tiles(screen: pygame.Surface, board: Board) -> None:
    """Draws on the screen of the tiles holder using the Board
    such that we have 20% of the vertical space being left for display of info"""
    width, height = screen.get_size()

    actual_height = 0.8 * height

    square_length = actual_height / board.get_rows()

    horizontal_start = (width - square_length * board.get_columns()) / 2

    # Draw rectangle
    for i in range(board.get_rows()):
        for j in range(board.get_columns()):
            x = horizontal_start + square_length * j
            y = square_length * i

            rect = pygame.Rect(x, y, square_length, square_length)
            pygame.draw.rect(screen, pygame.colordict.THECOLORS[TILE_COLOR], rect)

    pygame.display.flip()


def draw_gridlines(screen: pygame.Surface, board: Board) -> None:
    """Draws on the screen using the Board such that we have 20% of the vertical space
    being left for display of info"""
    width, height = screen.get_size()

    actual_height = 0.8 * height

    square_length = actual_height / board.get_rows()

    horizontal_start = (width - square_length * board.get_columns()) / 2

    # Draw vertical lines
    for i in range(board.get_columns() + 1):
        start_pos = (horizontal_start + i * square_length, 0)
        end_pos = (horizontal_start + i * square_length, (board.get_rows()) * square_length)

        pygame.draw.line(screen, pygame.colordict.THECOLORS[GRID_COLOR], start_pos, end_pos)

    # Draw horizontal lines
    for i in range(board.get_rows() + 1):
        start_pos = (horizontal_start, square_length * i)
        end_pos = (horizontal_start + (board.get_columns()) * square_length, square_length * i)

        pygame.draw.line(screen, pygame.colordict.THECOLORS[GRID_COLOR], start_pos, end_pos)

    pygame.display.flip()


def draw_text(screen: pygame.Surface, text: str, pos: tuple[int, int],
              color: str) -> None:
    """Draw the given text with the given color to the pygame screen at the given position.

    pos represents the *upper-left corner* of the text.
    """
    font = pygame.font.SysFont('inconsolata', 22)
    text_surface = font.render(text, True, pygame.colordict.THECOLORS[color])
    width, height = text_surface.get_size()
    screen.blit(text_surface,
                pygame.Rect(pos, (pos[0] + width, pos[1] + height)))


def update_tile(screen: pygame.Surface, row: int, column: int, board: Board) -> bool:
    """Updates the display of the given tile in the screen
    Returns if the game ended or not
    """
    if board.get_flag(row, column) or board.get_open(row, column):
        return False

    width, height = screen.get_size()

    actual_height = 0.8 * height

    square_length = actual_height / board.get_rows()

    horizontal_start = (width - square_length * board.get_columns()) / 2

    val = board.get_tile(row, column)
    x = int(horizontal_start + column * square_length)
    y = int(row * square_length)

    board.update_open(row, column)

    rect = pygame.Rect(x, y, square_length, square_length)
    pygame.draw.rect(screen, pygame.colordict.THECOLORS[OPEN_TILE_COLOR], rect)

    if val == '0':

        pygame.display.flip()
        return False

    elif val == 'B':

        x += square_length // 2
        y += square_length // 2

        radius = square_length * 0.25

        pygame.draw.circle(screen, pygame.colordict.THECOLORS[MINE_COLOR], (x, y), radius)

        pygame.display.flip()
        return True

    else:

        # Trying to make the font centered
        x += square_length * 0.4
        y += square_length * 0.4

        draw_text(screen, val, (x, y), NUMBER_COLORS[val])

        pygame.display.flip()
        return False


def update_flag(screen: pygame.Surface, row: int, column: int, board: Board) -> None:
    """Draws a flag on the specified tile"""
    if board.get_open(row, column):
        return

    width, height = screen.get_size()

    actual_height = 0.8 * height

    square_length = actual_height / board.get_rows()

    horizontal_start = (width - square_length * board.get_columns()) / 2

    x = int(horizontal_start + column * square_length) + square_length * 0.2
    y = int(row * square_length) + square_length * 0.2

    if board.get_flag(row, column):
        # Draw the tile back
        x = horizontal_start + square_length * column
        y = square_length * row

        rect = pygame.Rect(x, y, square_length, square_length)
        pygame.draw.rect(screen, pygame.colordict.THECOLORS[TILE_COLOR], rect)

    else:
        # Draw the flag
        rect = pygame.Rect(x, y, square_length * 0.6, square_length * 0.6)

        pygame.draw.rect(screen, pygame.colordict.THECOLORS[FLAG_COLOR], rect)

    board.update_flag(row, column)

    pygame.display.flip()


def handle_mouse_click(screen: pygame.Surface, event: pygame.event.Event,
                       screen_size: Tuple[int, int], board: Board) -> bool:
    """Handle a mouse click event.

    A pygame mouse click event object has two attributes that are important for this method:
        - event.pos: the (x, y) coordinates of the mouse click
        - event.button: an int representing which mouse button was clicked.
                        1: left-click, 3: right-click

    Returns True if the game ended and False otherwise
    """

    x, y = event.pos

    width, height = screen.get_size()

    actual_height = 0.8 * height

    rows = board.get_rows()
    cols = board.get_columns()

    square_length = actual_height / board.get_rows()

    horizontal_start = (width - square_length * board.get_columns()) / 2

    x_intervals = [horizontal_start + square_length * _ for _ in range(cols + 1)]
    y_intervals = [square_length * _ for _ in range(rows + 1)]

    row, col = None, None

    for i in range(cols):
        if x_intervals[i] <= x <= x_intervals[i + 1]:
            col = i
            break

    for j in range(rows):
        if y_intervals[j] <= y <= y_intervals[j + 1]:
            row = j
            break

    if row is not None and col is not None:
        if event.button == 1:
            return update_tile(screen, row, col, board)

        elif event.button == 3:
            update_flag(screen, row, col, board)


def main() -> None:
    """Runs the actual game"""
    board = Board(BOARD_ROWS, BOARD_COLUMNS, NUM_BOMBS)

    screen = initialize_screen()

    draw_tiles(screen, board)

    draw_gridlines(screen, board)

    while True:
        pygame.display.flip()

        event = pygame.event.wait()

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Call the event handling method
            handle_mouse_click(screen, event, screen.get_size(), board)

            draw_gridlines(screen, board)
        elif event.type == pygame.QUIT:
            break

    pygame.display.quit()


if __name__ == '__main__':
    main()

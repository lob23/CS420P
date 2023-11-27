import pygame
from utils.read_file import read_file
from level1.__init__ import level1

WIDTH = 600
WIN = pygame.display.set_mode((WIDTH + 200, WIDTH))
pygame.display.set_caption("Path Finding")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Spot:
    def __init__(self, row, col, width, total_rows, total_columns):
        self.row = row
        self.col = col
        self.x = col * width
        self.y = row * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self.total_columns = total_columns

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win, grid_start_x, grid_start_y):
        pygame.draw.rect(win, self.color, ( self.x + grid_start_x, self.y + grid_start_y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

        def __lt__(self, other):
            return False


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


def gap_fn(rows, column, width):
    if rows >= column:
        gap = width // rows
    else:
        gap = width // column
    return gap


def make_grid(rows, column, width):
    grid = []
    gap = gap_fn(rows, column, width)
    for i in range(rows):
        grid.append([])
        for j in range(column):
            spot = Spot(i, j, gap, rows, column)
            grid[i].append(spot)
    return grid


def draw_grid(win, rows, column, width, grid_start_x, grid_start_y):
    gap = gap_fn(rows, column, width)
    for i in range(rows + 1):
        pygame.draw.line(win, GREY, (grid_start_x, grid_start_y + i * gap),
                         (grid_start_x + column * gap, grid_start_y + i * gap))
        for j in range(column + 1):
            pygame.draw.line(win, GREY, (j * gap + grid_start_x, grid_start_y),
                             (grid_start_x + j * gap, grid_start_y + rows * gap))


def draw(win, grid, rows, column, width, grid_start_x, grid_start_y):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win, grid_start_x, grid_start_y)

    draw_grid(win, rows, column, width, grid_start_x, grid_start_y)
    pygame.display.update()


def main(win, width):
    level1(win, width, make_grid, draw)


main(WIN, WIDTH)

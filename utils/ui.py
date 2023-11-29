# Desc: UI utilities
import pygame


WIDTH = 600
WIN = pygame.display.set_mode((WIDTH + 300, WIDTH))
pygame.display.set_caption("Path Finding")
FPS = 60

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

pygame.font.init()
font = pygame.font.SysFont('freesansbold', 24)



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

class Button:
    def __init__(self, txt, pos):
        self.text = txt
        self.pos = pos
        self.button = pygame.rect.Rect((self.pos[0], self.pos[1]), (260, 40))

    def draw(self):
        pygame.draw.rect(WIN, 'light gray', self.button, 0, 5)
        pygame.draw.rect(WIN, 'dark gray', [self.pos[0], self.pos[1], 260, 40], 5, 5)
        text2 = font.render(self.text, True, 'black')
        WIN.blit(text2, (self.pos[0] + 15, self.pos[1] + 7))

    def check_clicked(self):
        if self.button.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            return True
        else:
            return False


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
    # win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win, grid_start_x, grid_start_y)

    draw_grid(win, rows, column, width, grid_start_x, grid_start_y)

    # if not menu:
    pygame.display.update()

def draw_menu():
    WIN.fill('white')
    command = -1
    pygame.draw.rect(WIN, 'black', [100, 100, 300, 300])
    pygame.draw.rect(WIN, 'green', [100, 100, 300, 300], 5)
    pygame.draw.rect(WIN, 'white', [120, 120, 260, 40], 0, 5)
    pygame.draw.rect(WIN, 'gray', [120, 120, 260, 40], 5, 5)
    txt = font.render('Menus!', True, 'black')
    WIN.blit(txt, (135, 127))
    # menu exit button
    menu = Button('Exit Menu', (120, 350))
    menu.draw()
    button1 = Button('Level 1', (120, 180))
    button1.draw()
    button2 = Button('Level 2', (120, 240))
    button2.draw()
    button3 = Button('Level 3', (120, 300))
    button3.draw()
    if menu.check_clicked():
        command = 0
    if button1.check_clicked():
        command = 1
    if button2.check_clicked():
        command = 2
    if button3.check_clicked():
        command = 3

    return command

def draw_menu_level1():
    command = -1
    # pygame.draw.rect(WIN, 'black', [100, 100, 300, 300])
    # pygame.draw.rect(WIN, 'green', [100, 100, 300, 300], 5)
    # pygame.draw.rect(WIN, 'white', [120, 120, 260, 40], 0, 5)
    # pygame.draw.rect(WIN, 'gray', [120, 120, 260, 40], 5, 5)
    # txt = font.render('Menus!', True, 'black')
    # WIN.blit(txt, (135, 127))
    # menu exit button
    exitButton = Button('Exit Menu', (620, 420))
    exitButton.draw()
    button1 = Button('Depth First Search', (620, 180))
    button1.draw()
    button2 = Button('Breadth First Search', (620, 240))
    button2.draw()
    button3 = Button('Uniform-Cost Search', (620, 300))
    button3.draw()
    button4 = Button('A star', (620, 360))
    button4.draw()
    if exitButton.check_clicked():
        command = 0
    if button1.check_clicked():
        command = 1
    if button2.check_clicked():
        command = 2
    if button3.check_clicked():
        command = 3
    if button4.check_clicked():
        command = 4

    return command

def draw_game():
    menu_btn = Button('Main Menu', (100, 100))
    menu_btn.draw()
    menu = menu_btn.check_clicked()
    return menu

# run = True
# main_menu = False
# menu_command = 0
# while run:
#     WIN.fill('white')
#     if main_menu:
#         menu_command = draw_menu()
#         if menu_command != -1:
#             main_menu = False
#     else:
#         main_menu = draw_game()
#         if menu_command > 0:
#             text = font.render(f'Button {menu_command} pressed!', True, 'black')
#             WIN.blit(text, (150, 100))
#
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             run = False
#
#     pygame.display.flip()
# pygame.quit()
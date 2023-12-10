# Desc: UI utilities
import pygame

# from level4.__init__ import Visualizer as Visualizerlv4

WIDTH = 600
WIN = pygame.display.set_mode((WIDTH + 300, WIDTH))
pygame.display.set_caption("Path Finding")
FPS = 60

# Colors
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
# Additional Colors
PINK = (255, 105, 180)
GOLD = (255, 223, 0)
SILVER = (192, 192, 192)
BROWN = (165, 42, 42)
TEAL = (0, 128, 128)
NAVY = (0, 0, 128)
MAROON = (128, 0, 0)
LIME = (0, 255, 0)
CORAL = (255, 127, 80)
INDIGO = (75, 0, 130)
# More colors


agent_color = [TEAL, TEAL, TURQUOISE, GREY, MAROON]


class UI:
    gap = 0


pygame.font.init()
font = pygame.font.SysFont('freesansbold', 24)


class Spot:
    num_agent = 0

    def __init__(self, row, col, width, total_rows, total_columns):
        self.name = None
        self.row = row
        self.col = col
        self.agent = None
        self.num_visited = 0
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
        self.color = NAVY

    def make_agent(self, agent):

        self.color = agent_color[int(agent[1])]
        self.name = agent

    def make_closed_agent(self, target):
        self.color = agent_color[int(target[1])]
        self.name = target

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_visited(self):
        self.num_visited += 1
        self.color = self.get_heatmap_color(self.num_visited / 20)

    def make_visited_key_door(self):
        self.color = LIME

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def make_key(self, key):
        self.color = PINK
        self.name = key

    def make_door(self, door):
        self.color = CORAL
        self.name = door

    def make_stair(self, stair):
        self.color = SILVER
        self.name = stair

    def get_heatmap_color(self, normalized_value_0_to_1):
        color1 = (255, 243, 59)  # Start color
        color2 = (233, 62, 58)  # End color

        # Interpolate between the two colors based on the normalized value
        r = int(color1[0] * (1 - normalized_value_0_to_1) + color2[0] * normalized_value_0_to_1)
        g = int(color1[1] * (1 - normalized_value_0_to_1) + color2[1] * normalized_value_0_to_1)
        b = int(color1[2] * (1 - normalized_value_0_to_1) + color2[2] * normalized_value_0_to_1)

        return r, g, b

    def draw(self, win, grid_start_x, grid_start_y):
        pygame.draw.rect(win, self.color, (self.x + grid_start_x, self.y + grid_start_y, self.width, self.width))

        if self.name is not None:
            font_scale = pygame.font.SysFont('freesansbold', int((UI.gap / 25) * 24))
            text = font_scale.render(self.name, True, 'black')
            #     the text align center
            WIN.blit(text, (self.x + grid_start_x + 2, self.y + grid_start_y + 2))

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
    UI.gap = gap
    print(UI.gap)
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


def draw_menu(url):
    WIN.fill('white')
    command = -1
    pygame.draw.rect(WIN, 'black', [100, 100, 300, 320])
    pygame.draw.rect(WIN, 'green', [100, 100, 300, 320], 5)
    pygame.draw.rect(WIN, 'white', [120, 120, 260, 40], 0, 5)
    pygame.draw.rect(WIN, 'gray', [120, 120, 260, 40], 5, 5)
    txt = font.render('Menus!', True, 'black')

    WIN.blit(txt, (135, 127))
    # menu exit button
    button1 = Button('Level 1', (120, 180))
    button2 = Button('Level 2', (120, 240))
    button3 = Button('Level 3', (120, 300))
    button4 = Button('Level 4', (120, 360))
    button5 = Button('Select File Again', (120, 420))
    if(url):
        button1.draw()
        button2.draw()
        button3.draw()
        button4.draw()
        if button4.check_clicked():
            command = 4
        if button1.check_clicked():
            command = 1
        if button2.check_clicked():
            command = 2
        if button3.check_clicked():
            command = 3
    button5.draw()
    if(button5.check_clicked()):
        command = 5

    return command


def draw_menu_level1():
    WIN.fill('white')
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


def print_score(visited=0):
    if visited is None:
        visitedtxt = font.render(f'Score: Cannot find any paths', True, 'black')
    else:
        visitedtxt = font.render(f'Score {100 - visited}', True, 'black')
    WIN.blit(visitedtxt, (620, 97))


def draw_menu_level2(visited=0):
    WIN.fill('white')
    command = -1
    exitButton = Button('Exit Menu', (620, 420))
    exitButton.draw()
    button1 = Button('Search', (620, 180))
    button1.draw()
    if exitButton.check_clicked():
        command = 0
    if button1.check_clicked():
        command = 1

    return command


def draw_menu_level3(floor=0, visited=0):
    WIN.fill('white')
    command = -1
    exitButton = Button('Exit Menu', (620, 420))
    exitButton.draw()
    floortxt = font.render(f'Current Floor {floor}', True, 'black')
    WIN.blit(floortxt, (620, 127))
    # visitedtxt = font.render(f'Score {100 - visited}', True, 'black')
    # WIN.blit(visitedtxt, (620, 97))
    button1 = Button('Search', (620, 180))
    button1.draw()
    # Go up floor
    button2 = Button('Go up floor', (620, 240))
    button2.draw()
    # Go down floor
    button3 = Button('Go down floor', (620, 300))
    button3.draw()

    if exitButton.check_clicked():
        command = 0
    if button1.check_clicked():
        command = 1
    if button2.check_clicked():
        command = 2
    if button3.check_clicked():
        command = 3
    # if button4.check_clicked():
    #     command = 4

    return command


def change_agent_and_redraw(grid, grid_start_x, grid_start_y):
    draw(WIN, grid, len(grid), len(grid[0]), WIDTH, grid_start_x, grid_start_y)


def draw_menu_level4(total_agent, agent=0, floor=0, visited=0):
    global agent_txt
    WIN.fill('white')
    command = -1
    exitButton = Button('Exit Menu', (620, 420))
    exitButton.draw()
    floortxt = font.render(f'Current Floor {floor}', True, 'black')
    WIN.blit(floortxt, (620, 127))
    if agent == 0:
        agent_txt = font.render(f'Agent: Print path', True, 'black')

    elif total_agent >= agent:
        agent_txt = font.render(f'Agent: {agent }', True, 'black')

    WIN.blit(agent_txt, (620, 67))
    button1 = Button('Search', (620, 180))
    button1.draw()
    # Go up floor
    button2 = Button('Go up floor', (620, 240))
    button2.draw()
    # Go down floor
    button3 = Button('Go down floor', (620, 300))
    button3.draw()
    # change agent
    button4 = Button('Change agent heatmap', (620, 360))
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

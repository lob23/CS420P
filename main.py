import pygame
from level1.__init__ import level1
from utils.ui import *


def main():
    clock = pygame.time.Clock()
    clock.tick(60)
    run = True
    main_menu = True
    menu_command = 0
    while run:
        menu_command = draw_menu()
        if menu_command == 1:
            level1()
        if menu_command == 2:
            print("level 2")
        if menu_command == 3:
            print("level 3")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        pygame.display.flip()


main()

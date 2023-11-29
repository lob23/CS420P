import pygame
from level1.__init__ import level1
from utils.ui import *


def main():
    clock = pygame.time.Clock()
    clock.tick(5)
    run = True
    main_menu = True
    menu_command = 0
    count = 0
    while run:
        menu_command = draw_menu()
        if menu_command == 1:
            level1()
            menu_command = -1
        if menu_command == 2:
            print("level 2")
            menu_command = -1

        if menu_command == 3:
            print("level 3")
            menu_command = -1
            count += 1
            print(count)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        pygame.display.flip()


main()

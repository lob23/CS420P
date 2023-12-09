import pygame
from level1.__init__ import level1
import level2.solution as level2
from level3.__init__ import level3
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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
            if pygame.MOUSEBUTTONDOWN:
                if menu_command == 1:
                    level1('level1/input.txt')
                elif menu_command == 2:
                    print("level 2")
                    level2.level2('src/maps/input.txt')
                    # level2.main()
                elif menu_command == 3:
                    print("level 3")
                    level3('src/maps/input.txt')
                    count += 1
                    print(count)
                elif menu_command == 4:
                    print("level 4")





        pygame.display.flip()


main()

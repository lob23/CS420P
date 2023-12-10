import pygame
from level1.__init__ import level1
import level2.solution as level2
from level3.__init__ import level3
from level4.__init__ import level4
from utils.ui import *
import tkinter
import tkinter.filedialog

# from PyQt5.QtWidgets import QDialog, QPushButton, QFileDialog, QApplication, QVBoxLayout
# import os
# import urllib.parse

def prompt_file():
    """Create a Tk file dialog and cleanup when finished"""
    top = tkinter.Tk()
    top.withdraw()  # hide window
    file_name = tkinter.filedialog.askopenfilename(parent=top)
    top.destroy()
    return file_name

# class SelectFile(QDialog):
#     def __init__(self):
#         super().__init__()
#         self.filename = None
#         self.init_ui()
#
#     def init_ui(self):
#         self.select_button = QPushButton("Select File")
#         self.select_button.clicked.connect(self.select_file)
#
#         self.layout = QVBoxLayout()
#         self.layout.addWidget(self.select_button)
#
#         self.setLayout(self.layout)
#
#     def select_file(self):
#         default_directory = os.getcwd()
#         filename, _ = QFileDialog.getOpenFileName(self, "Select File",default_directory)
#         if filename:
#             print(f"Selected file: {filename}")
#             self.filename = filename
#             self.close()
            
# def get_file():
#     app = QApplication([])
#     window = SelectFile()
#     window.show()
#     app.exec_()
#     url = window.filename
#     return url

def main():
    url = None
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
                    url = prompt_file()
                    # url = get_file()
                    if not url:
                        break
                    level1(url)
                elif menu_command == 2:
                    # url = get_file()
                    url = prompt_file()

                    if not url:
                        break
                    print("level 2")
                    level2.level2(url)
                    # level2.main()
                elif menu_command == 3:
                    # url = get_file()
                    url = prompt_file()

                    if not url:
                        break
                    print("level 3")
                    level3(url)
                    count += 1
                    print(count)
                elif menu_command == 4:
                    # url = get_file()
                    url = prompt_file()

                    if not url:
                        break
                    level4(url)
                    # level4('level4/test.txt')
                    print("level 4")
                    
        pygame.time.delay(100)
        pygame.display.flip()


main()

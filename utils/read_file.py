import re


def read_file(url):
    # Open file and read the content
    f = open(url)
    file_content = f.read()
    # Split the content into lines
    lines = file_content.strip().split('\n')

    # Initialize variables to store the current state while parsing
    floor_data = {}
    current_floor = None
    current_floor_data = []
    width, height = 0, -2
    current_row = -1
    for line in lines:
        if current_row == height:
            floor_data[current_floor] = {
                'width': width,
                'height': height,
                'floor_data': current_floor_data
            }
            current_floor_data = []
            current_row = -1

        if current_row == -1:
            current_row = 0
            height, width = map(int, line.split(','))
            continue

        if '[' in line and ']' in line:
            current_floor = line.strip('[]')
        else:
            row = []
            for x in line.split(','):
                row.append(x)
            current_floor_data.append(row)
            current_row += 1

    # Save the last floor data
    if current_floor is not None:
        floor_data[current_floor] = {
            'width': width,
            'height': height,
            'floor_data': current_floor_data
        }
    return floor_data


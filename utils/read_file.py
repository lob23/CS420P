import copy


def find_agent_and_task(row: list[str], current_row: int, current_floor_index: int, at_pairs: dict):
    for i, e in enumerate(row):
        if e.startswith('A'):
            at_pairs.update({e: (current_row, i, current_floor_index)})
        elif e.startswith('T'):
            at_pairs.update({e: (current_row, i, current_floor_index)})


def read_file(url):
    # Open file and read the content
    f = open(url)
    file_content = f.read()
    # Split the content into lines
    lines = file_content.strip().split('\n')

    # Initialize variables to store the current state while parsing
    floor_data = {}
    current_floor = None
    current_floor_index = 0
    current_floor_data = []
    width, height = 0, -2
    current_row = -1
    at_pairs = {}
    for line in lines:
        if current_row == height:
            floor_data[current_floor] = {
                'width': width,
                'height': height,
                'floor_data': current_floor_data,
            }
            current_floor_data = []
            current_row = -1

        if current_row == -1:
            current_row = 0
            height, width = map(int, line.split(','))
            continue

        if line.startswith('[') and line.endswith(']'):
            current_floor = line.strip('[]')
            current_floor_index += 1
        else:
            row = line.split(',')
            find_agent_and_task(row, current_row, current_floor_index, at_pairs)
            current_floor_data.append(row)
            current_row += 1

    # Save the last floor data
    if current_floor is not None:
        floor_data[current_floor] = {
            'width': width,
            'height': height,
            'floor_data': current_floor_data,
        }
    floor_data['at_pairs'] = at_pairs
    return floor_data

# print(read_file('../level1/input.txt'))
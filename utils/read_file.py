import copy
import re


# atkds: agent, task, key, door, stairs
def find_agent_and_task(row: list[str], current_row: int, current_floor_index: int, atkds: dict):
    for i, e in enumerate(row):
        if e.startswith('A') or e.startswith('K') or e.startswith('T'):
            atkds.update({e: (current_row, i, current_floor_index)})
        elif re.search(r'^D\d+$', e) is not None:
            if e not in atkds:
                atkds[e] = []
            atkds[e].append((current_row, i, current_floor_index))
        elif e == 'DO' or e == 'UP':
            stair = e + str(current_floor_index)
            if stair not in atkds:
                atkds[stair] = []
            atkds[stair].append((current_row, i, current_floor_index))


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
    atkds = {}
    for i, line in enumerate(lines):
        if i == 0:
            height, width = map(int, line.split(','))
            continue

        if line.startswith('[') and line.endswith(']'):
            current_floor = line.strip('[]')
            current_floor_index += 1
        else:
            row = line.split(',')
            count = (i % (height + 1)) - 2
            col = height - 1 if count == -2 else count
            find_agent_and_task(row, col, current_floor_index, atkds)
            current_floor_data.append(row)
        if i % (height + 1) == 0:
            floor_data[current_floor] = {
                'width': width,
                'height': height,
                'floor_data': current_floor_data,
            }
            current_floor_data = []
    floor_data['atkds'] = atkds
    return floor_data

# Text read file
# print(read_file('../level1/input.txt'))
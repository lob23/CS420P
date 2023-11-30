import heapq

def manhattan_distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def get_neighbors(grid, position, keys):
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Up, Down, Right, Left
    neighbors = []
    for dx, dy in directions:
        x, y = position[0] + dx, position[1] + dy
        if 0 <= x < len(grid) and 0 <= y < len(grid[0]):
            cell = grid[x][y]
            if cell == '-' or (cell.startswith('D') and cell[1:] not in keys):
                continue  # Wall or locked door
            neighbors.append((x, y))
    return neighbors

def a_star_search(grid, start, goal, doors_keys):
    # Priority queue: (cost, position, keys_collected)
    pq = [(0, start, frozenset())]
    visited = set()

    while pq:
        cost, position, keys = heapq.heappop(pq)

        if position == goal:
            return cost  # Reached the goal

        if (position, keys) in visited:
            continue

        visited.add((position, keys))

        for neighbor in get_neighbors(grid, position, keys):
            new_cost = cost + 1  # Add the cost for moving to the neighbor
            new_keys = keys

            # Collect key if present
            if grid[neighbor[0]][neighbor[1]].startswith('K'):
                new_keys = keys | {grid[neighbor[0]][neighbor[1]][1:]}

            # Add neighbor to the queue with updated cost and keys
            heapq.heappush(pq, (new_cost + manhattan_distance(neighbor, goal), neighbor, new_keys))

    return -1  # No path found

# Example Grid
grid = [
    ["0", "0", "D1", "0", "K1"],
    ["-", "0", "-", "0", "0"],
    ["0", "K1", "-", "0", "T1"]
]

start = (0, 0)  # Starting position of the agent
goal = (2, 4)  # Mr. Thanh's position (T1)

# Mapping of doors to keys (assuming keys and doors are uniquely paired)
doors_keys = {'D1': 'K1'}

# Perform A* search
path_cost = a_star_search(grid, start, goal, doors_keys)
print(f"Path cost to reach the goal: {path_cost}")

assignments = []

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s + t for s in A for t in B]

rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
# Create extra units for diagonal rules
diagonal_units = [[r + c for r, c in zip('ABCDEFGHI','123456789')], [r + c for r, c in zip('ABCDEFGHI','987654321')]]
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], []))-{s}) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    for unit in unitlist:
        for box in unit:
            if len(values[box]) != 2:
                continue
            for neighbor in unit:
                if neighbor == box:
                    continue
                if values[neighbor] == values[box]:
                    # Replace all other boxes in this unit except the twins
                    peers = {p for p in unit if p not in {box, neighbor}}
                    for peer in peers:
                        assign_value(values, peer, values[peer].replace(values[box][0], '').replace(values[box][1], ''))
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    assert (len(grid) == 81)
    return {box: grid[i] if grid[i] != '.' else '123456789' for i, box in enumerate(boxes)}

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    for box, value in values.items():
        if len(value) == 1:
            continue
        else:
            box_peers = peers[box]
            for peer in box_peers:
                if len(values[peer]) == 1:
                    assign_value(values, box, values[box].replace(values[peer], ''))
    return values

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        for box in unit:
            if len(values[box]) == 1:
                continue
            value = values[box]
            for neighbor in unit:
                if neighbor == box:
                    continue
                for peer_value in values[neighbor]:
                    value = value.replace(peer_value, '')
            if len(value) == 1:
                peer_values = {values[peer] for peer in peers[box]}
                # If the only choice left is not a valid choice, return empty string.
                if value in peer_values:
                    assign_value(values, box, '')
                else:
                    assign_value(values, box, value)
    return values

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Use the Naked Twins Strategy
        # ßvalues = naked_twins(values)

        # Use the Eliminate Strategy
        values = eliminate(values)

        # Use the Only Choice Strategy
        values = only_choice(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if not values:
        return False
    unsolved = [box for box in values.keys() if len(values[box]) > 1]
    if len(unsolved) == 0:
        return values
    # Choose one of the unfilled squares with the fewest possibilities
    branch_root = sorted(unsolved, key=lambda k: len(values[k]))[0]
    root_values = values[branch_root]

    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for v in root_values:
        values_ = values.copy()
        assign_value(values_, branch_root, v)
        solution = search(values_)
        if solution:
            return solution

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')

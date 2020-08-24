import numpy as np

def pp_str(o):
    if o is None:
        s = '<none>'
    else:
        s = str(o)
    if '\n' in s:
        s = s.split('\n')[0] + '...'
    if len(s) > 30:
        s = s[:27] + '...'
    return s

def pp_display(data):
    if len(data) > 10:
        # squeeze vertically
        height = 12
        vertical_indices = tuple(range(7)) + (-1,) + (len(data) - 2, len(data) - 1)
    else:
        height = len(data) + 2
        vertical_indices = range(len(data))
    titles = data.dtype.names
    grid = np.empty((height,len(titles)), dtype=object)
    # column titles
    grid[0] = data.dtype.names
    # underlines
    grid[1] = tuple('-'*len(title) for title in titles)
    # data
    for grid_i, i in enumerate(vertical_indices):
        if i == -1:
            # vertical squeeze indicator
            grid[grid_i+2] = ('...',)*len(titles)
        else:
            grid[grid_i+2] = tuple(pp_str(o) for o in data[i].tolist())
    # check width
    col_width = np.array(list(max(map(len, grid[:,j])) for j in range(len(titles))))
    col_width[:-1] += 2
    cum_width = np.cumsum(col_width)
    width_overflow_idx = np.searchsorted(cum_width, 100)
    if width_overflow_idx < len(titles):
        # squeeze horizontally
        grid[:,width_overflow_idx] = '...'
        col_width[width_overflow_idx] = 3
        grid = grid[:,:width_overflow_idx+1]
        col_width = col_width[:width_overflow_idx+1]
    # display
    output = []
    for row in grid:
        for elem, col_w in zip(row, col_width):
            output.append(elem + (col_w - len(elem)) * ' ')  
        output.append('\n')
    return ''.join(output[:-1])


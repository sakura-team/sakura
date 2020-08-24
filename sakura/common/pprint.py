import numpy as np
from sakura.common.colors import Colors

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

def pp_display_dataframe(data, exact_len=None, offset=0,
                max_width=100, max_height=12, split_ratio=0.7):
    data_len = len(data)
    if exact_len is None:
        exact_len = data_len
    if data_len - offset > max_height - 2:
        # squeeze vertically
        grid_h = max_height
        num_start_items = int((max_height - 2) * split_ratio)
        num_end_items = max_height - 3 - num_start_items
        vertical_indices = tuple(range(offset, offset + num_start_items)) + (-1,) + \
                           tuple(range(data_len-num_end_items, data_len))
    else:
        # if data_len is low, we might actually reduce the requested offset
        # because we can display more data.
        offset = max(0, min(offset, data_len - max_height + 2))
        grid_h = data_len + 2
        vertical_indices = range(offset, data_len)
    titles = data.dtype.names
    grid_w = 1 + len(titles)
    grid = np.empty((grid_h,grid_w), dtype=object)
    row_colors = []
    # column titles
    grid[0] = ('',) + data.dtype.names
    row_colors.append(Colors.DEFAULT)
    # underlines
    grid[1] = ('',) + tuple('-'*len(title) for title in titles)
    row_colors.append(Colors.DEFAULT)
    # data
    for grid_i, i in enumerate(vertical_indices):
        if i == -1:
            # vertical squeeze indicator
            grid[grid_i+2] = ('...',) * grid_w
            row_colors.append(Colors.DEFAULT)
        else:
            grid[grid_i+2] = ('#' + str(i),) + tuple(pp_str(o) for o in data[i].tolist())
            row_colors.append(Colors.DEFAULT if i < exact_len else Colors.RED)
    # check width
    col_width = np.array(list(max(map(len, grid[:,j])) for j in range(grid_w)))
    col_width[1:] += 2     # 2 spaces between columns
    cum_width = np.cumsum(col_width)
    width_overflow_idx = np.searchsorted(cum_width, 100)
    if width_overflow_idx < grid_w:
        # squeeze horizontally
        grid[:,width_overflow_idx] = '...'
        col_width[width_overflow_idx] = 3
        grid = grid[:,:width_overflow_idx+1]
        col_width = col_width[:width_overflow_idx+1]
    # display
    output = []
    for row_i, row in enumerate(grid):
        output.append(row_colors[row_i])
        for elem, col_w in zip(row, col_width):
            output.append((col_w - len(elem)) * ' ' + elem)
        output.append(Colors.RESET + '\n')
    return ''.join(output)[:-1] # remove ending \n


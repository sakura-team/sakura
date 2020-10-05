import numpy as np
from sakura.common.colors import Colors
from sakura.common.term import term_length, term_truncate

def pp_str(o):
    if o is None:
        s = '<none>'
    else:
        s = str(o)
    s = s.replace('\n', r'\n')
    return s

# space between columns
SPACING = 2
# do not try to reduce width of a column below this size
MIN_COL_WIDTH = 10
# if we exclude right columns, we will have to display
# a column with '...' of this size (spacing including)
SQUEEZE_COL_WIDTH = SPACING + len('...')

def fix_col_width(col_width, max_width):
    # first column (indices) should not be abbreviated
    first_col_width = col_width[0]
    col_width = col_width[1:]
    max_width -= first_col_width
    # if too many large columns discard columns on the right
    if np.minimum(col_width, MIN_COL_WIDTH).sum() > max_width:
        col_width = col_width[:-1]
        while np.minimum(col_width, MIN_COL_WIDTH).sum() + SQUEEZE_COL_WIDTH > max_width:
            col_width = col_width[:-1]
        max_width -= SQUEEZE_COL_WIDTH
    # reduce size of largest columns until we can fit max_width
    while col_width.sum() > max_width:
        c_max = col_width.max()
        c_sum = col_width.sum()
        max_num_reduced_cols = c_sum // c_max
        removal = (c_sum - max_width) // max_num_reduced_cols
        if removal == 0:
            removal = 1
        col_width = np.minimum(col_width, c_max-removal)
    # restore first column
    col_width = np.insert(col_width, 0, first_col_width)
    return col_width

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
    orig_col_width = np.array(list(max(map(term_length, grid[:,j])) for j in range(grid_w)))
    orig_col_width[1:] += SPACING     # spaces between columns
    col_width = fix_col_width(orig_col_width, max_width) # deal with max_width
    width_overflow_idx = len(col_width)
    if width_overflow_idx < grid_w:
        # squeeze horizontally
        grid[:,width_overflow_idx] = '...'
        col_width[width_overflow_idx] = SQUEEZE_COL_WIDTH
        grid = grid[:,:width_overflow_idx+1]
    # display
    output = []
    for row_i, row in enumerate(grid):
        output.append(row_colors[row_i])
        for col_i, elem_info in enumerate(zip(row, col_width)):
            elem, col_w = elem_info
            elem_max_w = col_w - (0 if col_i == 0 else SPACING)
            elem_w, elem = term_truncate(elem, elem_max_w, truncate_sign='...')
            output.append((col_w - elem_w) * ' ' + elem)
        output.append(Colors.RESET + '\n')
    return ''.join(output)[:-1] # remove ending \n


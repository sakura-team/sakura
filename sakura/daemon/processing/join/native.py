
def native_join(left_s, right_s, left_col, right_col):
    left_join_id = left_s.get_native_join_id()
    right_join_id = right_s.get_native_join_id()
    if left_join_id is None or right_join_id is None or left_join_id != right_join_id:
        # cannot do a native join with these sources
        return None
    return left_s._native_join(right_s, left_col, right_col)

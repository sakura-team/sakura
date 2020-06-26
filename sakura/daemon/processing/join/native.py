
def native_join(left_s, right_s, left_col, right_col):
    # if left or right source have an offset or a limit, prevent native join.
    # on an SQL query, this is this kind of case:
    # select * from (select * from t1 limit 5) as t1_limited, t2 where t1_limited.id = t2.id
    # and it prevents being able to join t1 and t2 directly.
    if left_s._offset > 0 or right_s._offset > 0:
        return None
    if left_s._limit is not None or right_s._limit is not None:
        return None
    # check if left and right sources are compatible for a native join
    left_join_id = left_s.get_native_join_id()
    right_join_id = right_s.get_native_join_id()
    if left_join_id is None or right_join_id is None or left_join_id != right_join_id:
        # cannot do a native join with these sources
        return None
    return left_s._native_join(right_s, left_col, right_col)

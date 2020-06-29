from sakura.daemon.processing.sources.base import SourceBase
from sakura.daemon.processing.condition import JoinCondition
from sakura.daemon.processing.join.native import native_join
from sakura.daemon.processing.join.merge import merge_join
from collections import defaultdict

# try native join first, merge join as a fallback
JOIN_METHODS = (native_join, merge_join)

class JoinSource(SourceBase):
    def __init__(self, label = '<join>'):
        SourceBase.__init__(self, label)
        self.data.sub_sources = ()
    def add_sub_source(self, source):
        self.data.sub_sources += (source,)
        for col in source.all_columns:
            self.all_columns.append(col)
        for col in source.columns:
            self.columns.append(col)
    def where(self, conds):
        source = self.reinstanciate()
        for cond in conds.list():
            sub_sources = source.data.sub_sources
            if isinstance(cond, JoinCondition):
                # verify this can be applied
                self.which_subsource(sub_sources, cond.left_col)
                self.which_subsource(sub_sources, cond.right_col)
                # ok
                source.join_conds += (cond,)
                # do not select both columns in output, since they are joined
                if cond.left_col in self.columns and cond.right_col in self.columns:
                    cols = (col for col in self.columns \
                            if col.get_uuid() != cond.right_col.get_uuid())
                    source = source.select(*cols)
            else:   # column filter
                sub_sources = cond.filtered_sources(*sub_sources)
                source.data.sub_sources = tuple(sub_sources)
        return source
    def join(self, other):
        join_source = self.reinstanciate()
        join_source.add_sub_source(other)
        return join_source
    def which_subsource(self, sub_sources, col):
        for sub_s in sub_sources:
            if col in sub_s:
                return sub_s
        raise APIRequestError('Column does not belong to this source.')
    def solve(self):
        sub_sources = self.data.sub_sources
        join_conds = self.join_conds
        for join_method in JOIN_METHODS:
            sub_sources, join_conds = self.solve_joins(sub_sources, join_conds, join_method)
        if len(sub_sources) > 1:
            raise APIRequestError('Missing one .where(<col1> == <col2>) join condition on this joint source.')
        source = sub_sources[0]
        source = source.offset(self._offset)
        source = source.limit(self._limit)
        return source.select(*self.columns)
    def solve_joins(self, sub_sources, join_conds, join_method):
        remaining_join_conds = ()
        for join_cond in join_conds:
            # retrieve left and right source of join
            left_col, right_col = join_cond.left_col, join_cond.right_col
            left_s = self.which_subsource(sub_sources, left_col)
            right_s = self.which_subsource(sub_sources, right_col)
            # if algorithm allows it, compute joint source
            source = join_method(left_s, right_s, left_col, right_col)
            if source is None:
                # this algorithm cannot join these sources
                remaining_join_conds += (join_cond,)
            else:
                # ok, algorithm did it
                # replace sources left_s and right_s with the new source
                sub_sources = tuple(s for s in sub_sources if s not in (left_s, right_s))
                sub_sources += (source,)
        return sub_sources, remaining_join_conds
    def sort(self, *columns):
        source = self.solve()
        return source.sort(*columns)
    def all_chunks(self, chunk_size = None):
        source = self.solve()
        return source.all_chunks(chunk_size)

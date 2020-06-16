import sys, traceback, sakura.daemon.conf as conf
from pathlib import Path
from sakura.common.errors import InputUncompatible
from sakura.daemon.processing.operator import Operator
from sakura.daemon.loading import load_datastores
from sakura.daemon.tools import NullContext
from sakura.daemon.code.git import get_worktree, list_code_revisions, list_operator_subdirs
from sakura.daemon.code.loading import load_op_class
from sakura.common.errors import APIOperatorError
from sakura.common.io import ORIGIN_ID
from contextlib import contextmanager

@contextmanager
def RedirectedStreams(streams):
    globals()['__streams__'] = streams
    try:
        yield
    finally:
        del globals()['__streams__']

class DaemonEngine(object):
    def __init__(self):
        self.datastores = {}
        for ds in load_datastores(self):
            ds = ds.adapter.adapt(self, ds)
            self.datastores[(ds.host, ds.driver_label)] = ds
        self.op_instances = {}
        self.hub = None
        self.name = conf.daemon_desc
        self.code_workdir = Path(conf.work_dir) / 'code'
        self.origin_id = ORIGIN_ID
        self.col_tags_info = {}
    def fire_data_issue(self, issue, should_fail=True):
        if should_fail:
            raise Exception(issue)
        else:
            sys.stderr.write(issue + '\n')
    def register_hub_api(self, hub_api):
        self.hub = hub_api
    def get_daemon_info_serializable(self):
        return dict(name=self.name,
                    datastores=tuple(ds.pack() for ds in self.datastores.values()),
                    origin_id = self.origin_id)
    def create_operator_instance(self, op_id, event_recorder, **repo_info):
        with self.redirected_streams(**repo_info):
            try:
                op_cls, op_dir = self.load_op_class(**repo_info)
                op = op_cls(op_id, event_recorder, op_dir)
                op.api = self.hub.operator_apis[op_id]
                op.construct()
            except BaseException as e:
                print('Operator ERROR detected!')
                traceback.print_exc()
                raise APIOperatorError(str(e))
            self.op_instances[op_id] = op
            print("created operator %s op_id=%d" % (op_cls.NAME, op_id))
    def delete_operator_instance(self, op_id):
        if op_id in self.op_instances:
            print("deleting operator %s op_id=%d" % (self.op_instances[op_id].NAME, op_id))
            del self.op_instances[op_id]
    def reload_operator_instance(self, op_id, event_recorder, **repo_info):
        self.delete_operator_instance(op_id)
        self.create_operator_instance(op_id, event_recorder, **repo_info)
    def is_foreign_operator(self, op_id):
        return op_id not in self.op_instances
    def connect_operators(self, src_op_id, src_out_id, dst_op_id, dst_in_id,
                            check_mode = False):
        if self.is_foreign_operator(src_op_id):
            # the source is a remote operator.
            src_label = 'remote(op_id=%d,out%d)' % (src_op_id, src_out_id)
            src_op = self.hub.context.op_instances[src_op_id]
        else:
            src_op = self.op_instances[src_op_id]
            src_label = '%s op_id=%d out%d' % (src_op.NAME, src_op_id, src_out_id)
        dst_op = self.op_instances[dst_op_id]
        dst_input_plug = dst_op.input_plugs[dst_in_id]
        dst_input_plug.connect(src_op.output_plugs[src_out_id])
        # auto select (or just check) unselected parameters
        if check_mode:   # just check, do not set parameters
            res = dst_op.check_input_compatibility_parameters(dst_input_plug)
            dst_input_plug.disconnect()     # revert
            return res
        else:
            print("connected %s -> %s op_id=%d in%d" % \
                (src_label, dst_op.NAME, dst_op_id, dst_in_id))
            dst_op.auto_fill_parameters(plug = dst_input_plug)
            return True
    def disconnect_operators(self, src_op_id, src_out_id, dst_op_id, dst_in_id):
        dst_op = self.op_instances[dst_op_id]
        dst_input_plug = dst_op.input_plugs[dst_in_id]
        dst_op.unselect_parameters(plug = dst_input_plug)
        dst_input_plug.disconnect()
        print("disconnected [...] -> %s op_id=%d in%d" % \
                (dst_op.NAME, dst_op_id, dst_in_id))
    def get_possible_links(self, src_op_id, dst_op_id):
        print('get_possible_links', src_op_id, dst_op_id)
        dst_op = self.op_instances[dst_op_id]
        dst_op.set_check_mode(True)
        if self.is_foreign_operator(src_op_id):
            src_op = self.hub.context.op_instances[src_op_id]
        else:
            src_op = self.op_instances[src_op_id]
        # check all src_op.output -> dst_op.input combinations
        # and discard those which cause an exception.
        links = []
        for dst_in_id, dst_input_plug in enumerate(dst_op.input_plugs):
            for src_out_id in range(len(src_op.output_plugs)):
                if dst_input_plug.connected():
                    # this entry is already connected with something else
                    continue
                checked = self.connect_operators(src_op_id, src_out_id, dst_op_id, dst_in_id,
                                                    check_mode = True)
                if checked:
                    # this link is possible
                    links.append((src_out_id, dst_in_id))
        dst_op.set_check_mode(False)
        print('found %d possible links' % len(links))
        return links
    def redirected_streams(self, local_streams = None, sandbox_streams = None, **kwargs):
        if local_streams is None:
            if sandbox_streams is None:
                return NullContext()
            else:
                return RedirectedStreams(sandbox_streams)
        else:
            return RedirectedStreams(local_streams)
    def load_op_class(self, code_subdir, repo_type, local_streams = None, sandbox_streams = None,  **other_repo_info):
        module_attributes = {}
        if repo_type == 'git':
            worktree_dir = get_worktree(
                        self.code_workdir,
                        other_repo_info['repo_url'],
                        other_repo_info['code_ref'],
                        other_repo_info['commit_hash'])
        elif repo_type == 'sandbox':
            worktree_dir = other_repo_info['sandbox_dir']
        if local_streams is not None:
            module_attributes.update(__streams__ = local_streams)
        elif sandbox_streams is not None:
            module_attributes.update(__streams__ = sandbox_streams)
        return load_op_class(worktree_dir, code_subdir, repo_type, **module_attributes)
    def get_op_class_metadata(self, code_subdir, **repo_info):
        with self.redirected_streams(**repo_info):
            op_cls, op_dir = self.load_op_class(code_subdir, **repo_info)
            metadata = dict(
                name = op_cls.NAME,
                tags = op_cls.TAGS,
                short_desc = op_cls.SHORT_DESC,
                svg = op_cls.ICON
            )
            if hasattr(op_cls, 'COMMIT_INFO'):
                metadata.update(
                    commit_metadata = op_cls.COMMIT_INFO
                )
            return metadata
    def prefetch_code(self, repo_url, code_ref, commit_hash):
        get_worktree(self.code_workdir, repo_url, code_ref, commit_hash)
    def list_code_revisions(self, repo_url, repo_subdir = None):
        return list_code_revisions(self.code_workdir, repo_url, repo_subdir = repo_subdir)
    def list_operator_subdirs(self, repo_url, code_ref):
        return list_operator_subdirs(self.code_workdir, repo_url, code_ref)
    def set_col_tags(self, col_tags_info):
        self.col_tags_info = col_tags_info

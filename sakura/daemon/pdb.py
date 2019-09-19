import sys

CURRENT_PDB_SESSION = None

def hook_pdb():
    import pdb
    class HookedPdb(pdb.Pdb):
        def set_trace(self, frame):
            global CURRENT_PDB_SESSION
            if CURRENT_PDB_SESSION is not None and CURRENT_PDB_SESSION is not self:
                print('-- pdb.set_trace() FAILED. --')
                print('Another developer is currently running a pdb session on the same sakura daemon.')
                print('Cannot run another concurrent session, sorry. Please retry later.')
                print('Continuing execution.')
                print('-----------------------------')
                return None
            CURRENT_PDB_SESSION = self
            super().set_trace(frame)
        def _release_session(self):
            global CURRENT_PDB_SESSION
            if CURRENT_PDB_SESSION is self:
                CURRENT_PDB_SESSION = None
        def set_continue(self):
            self._release_session()
            return super().set_continue()
        def __del__(self):
            self._release_session()
            if hasattr(super(), '__del__'):
                super().__del__()
    pdb.Pdb = HookedPdb

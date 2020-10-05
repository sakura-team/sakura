import gevent, sys, socket
from bisect import bisect_right
from gevent.queue import Queue, Empty
from gevent.socket import wait_read
from sakura.common.chunk import NumpyChunk
from sakura.common.pprint import pp_display_dataframe
from sakura.common.colors import Colors
from sakura.common.exactness import EXACT, APPROXIMATE
from sakura.common.term import TTYSettings
from sakura.client.shelltools import StdinMonitor, interruptible_queue_get
from sakura.client.stream import StreamBgThread

SCROLL_HELP = '<up>/<down>, <page-up>/<page-down>: scroll'
Q_HELP = '<q>: quit'

class ResultSetBGThread:
    def __init__(self, dtype):
        self.dtype = dtype
        self._exact_chunks = []
        self._exact_chunks_indices = []
        self._exact_len = 0
        self._approximate_chunk = None
        self._ready = False
        self._show_offset = 0
        self.queue = Queue()
    def get_status(self):
        desc = ''
        if len(self) == 0:
            if self._ready is True:
                desc += 'Fully retrieved, but empty.'
            else:
                desc += 'COMPUTING PREVIEW, empty for now.'
        else:
            if self._ready is True:
                desc += 'Fully retrieved.'
            else:
                desc += 'PARTIALLY retrieved.'
        if self._approximate_chunk is not None:
            if self._exact_len == 0:
                desc += ' All computed rows '
            else:
                desc += f' Rows at #{self._exact_len} and more '
            desc += f'are {Colors.RED}approximate{Colors.RESET}.'
        return desc
    def update_repr(self):
        if len(self) == 0:
            self._current_repr = self.get_status()
        else:
            tty = TTYSettings()
            self._current_repr = '\n\n'.join((
                pp_display_dataframe(self, exact_len=self._exact_len, max_width = tty.cols),
                self.get_status()
            ))
    def compute_show_view(self):
        tty = TTYSettings()
        dataframe_text = pp_display_dataframe(
                self,
                exact_len=self._exact_len,
                offset = self._show_offset,
                max_height = tty.rows - 4,
                max_width = tty.cols)
        lines = dataframe_text.split('\n')
        if len(lines) < tty.rows - 4:
            lines += [ '' ] * (tty.rows - 4 - len(lines))
        separator = '\u2501' * tty.cols
        help_line = '  ' + SCROLL_HELP + ' \u2502 ' + Q_HELP + '\r'
        lines = [ 'Status: ' + self.get_status(), separator ] + \
                lines + \
                [ separator + help_line ]
        return '\r\n'.join(lines)
    def inc_show_offset(self, inc_value):
        offset = self._show_offset + inc_value
        offset = min(offset, len(self) - self.get_show_page_len())
        offset = max(offset, 0)
        if offset == self._show_offset:
            return False    # offset did not change
        else:
            self._show_offset = offset
            return True
    def get_show_page_len(self):
        tty = TTYSettings()
        return tty.rows - 6     # only data view, without column titles
    def on_change(self):
        self.update_repr()
        self._data_cache = None
    def __len__(self):
        total_len = self._exact_len
        if self._approximate_chunk is not None:
            total_len += len(self._approximate_chunk)
        return total_len
    def __getitem__(self, i):
        if i < 0 or i >= len(self):
            raise IndexError
        if i < self._exact_len:
            chunk_idx = bisect_right(self._exact_chunks_indices, i) - 1
            pos_in_chunk = i - self._exact_chunks_indices[chunk_idx]
            return self._exact_chunks[chunk_idx][pos_in_chunk]
        else:
            return self._approximate_chunk[i - self._exact_len]
    def data(self):
        if self._data_cache is not None:
            return self._data_cache
        total_len = len(self)
        warnings = []
        if not self._ready:
            warnings.append(
                'Warning: resultset is not complete (partially retrieved).')
        if self._approximate_chunk is not None:
            warnings.append(f'Warning: resultset is '
                            f'{Colors.RED}approximate{Colors.RESET} '
                            f'(from row #{self._exact_len}).')
        # simple cases first
        if len(self._exact_chunks) == 1 and self._approximate_chunk is None:
            total_chunk = self._exact_chunks[0]
        elif len(self._exact_chunks) == 0 and self._approximate_chunk is not None:
            total_chunk = self._approximate_chunk
        else: # general case
            total_chunk = NumpyChunk.empty(total_len, self.dtype, EXACT)
            for chunk, idx in zip(self._exact_chunks, self._exact_chunks_indices):
                total_chunk[idx:idx+len(chunk)] = chunk
            if self._approximate_chunk is not None:
                total_chunk[self._exact_len:] = self._approximate_chunk
                total_chunk.exactness = APPROXIMATE
            # avoid to redo this work next time
            if self._exact_len > 0:
                self._exact_chunks = [ total_chunk[:self._exact_len] ]
                self._exact_chunks_indices = [ 0 ]
            if self._approximate_chunk is not None:
                self._approximate_chunk = total_chunk[self._exact_len:]
        self._data_cache = { 'status': 'ok', 'data': total_chunk, 'warnings': warnings, 'ready': self._ready }
        return self._data_cache
    def run(self, bg_queue, init_queue):
        self.on_change()
        init_queue.put(1)   # unblock init
        data_waiter, snapshoter, show_waiter, previewer = None, None, None, None
        while not self._stopped:
            # handle events
            show_needs_update = False
            evt_args = bg_queue.get()
            if evt_args[0] == 'SET_DATA_WAITER':
                if not self._ready:
                    print('Waiting for full dataset computation/retrieval...')
                data_waiter = evt_args[1]
            elif evt_args[0] == 'REMOVE_DATA_WAITER':
                data_waiter = None
            elif evt_args[0] == 'SET_DATA_SNAPSHOTER':
                snapshoter = evt_args[1]
            elif evt_args[0] == 'REMOVE_DATA_SNAPSHOTER':
                snapshoter = None
            elif evt_args[0] == 'SET_PREVIEW_WAITER':
                previewer = evt_args[1]
            elif evt_args[0] == 'REMOVE_PREVIEW_WAITER':
                previewer = None
            elif evt_args[0] == 'SET_SHOW_WAITER':
                show_waiter = evt_args[1]
                show_needs_update, self._show_offset = True, 0
            elif evt_args[0] == 'INC_SHOW_OFFSET':
                show_needs_update |= self.inc_show_offset(1)
            elif evt_args[0] == 'DEC_SHOW_OFFSET':
                show_needs_update |= self.inc_show_offset(-1)
            elif evt_args[0] == 'INC_SHOW_PAGE':
                show_needs_update |= self.inc_show_offset(self.get_show_page_len())
            elif evt_args[0] == 'DEC_SHOW_PAGE':
                show_needs_update |= self.inc_show_offset(-1 * self.get_show_page_len())
            elif evt_args[0] == 'REMOVE_SHOW_WAITER':
                show_waiter = None
            elif evt_args[0] == 'CHUNK':
                chunk = evt_args[1]
                if chunk.exact():
                    self._exact_chunks.append(chunk)
                    self._exact_chunks_indices.append(self._exact_len)
                    self._exact_len += len(chunk)
                    self._approximate_chunk = None
                else:
                    self._approximate_chunk = chunk
                self.on_change()
                show_needs_update = True
            elif evt_args[0] == 'STREAM_END':
                self._ready = True
                self.on_change()
                show_needs_update = True
            if show_waiter is not None and show_needs_update:
                show_waiter.put(('SHOW_VIEW', self.compute_show_view()))
            # handle snapshoter
            if snapshoter is not None:
                snapshot_info = self.data()
                snapshoter.put(snapshot_info)
                snapshoter = None
            # handle data_waiter
            if self._ready and data_waiter is not None:
                data = self.data()
                data_waiter.put(data)
                data_waiter = None
            # handle previewer
            if previewer is not None:
                # if we already got at least one chunk (or end-of-stream notification)
                if self._ready or len(self) > 0:
                    previewer.put(0)    # unblock
                    previewer = None
    def spawn(self):
        self._stopped = False
        init_queue = Queue()
        gevent.spawn(self.run, self.queue, init_queue)
        init_queue.get()    # wait until bg greenlet has done the init
    def stop(self):
        self._stopped = True

class ResultSet:
    def __init__(self, dtype, it):
        self._resultset_bg_thread = ResultSetBGThread(dtype)
        self._stream_bg_thread = StreamBgThread(it, self._resultset_bg_thread.queue)
        self._spawn()
    def snapshot(self):
        return self._data('DATA_SNAPSHOTER')
    def data(self):
        self._stream_bg_thread.start()
        return self._data('DATA_WAITER')
    def _request(self, waiter_type, timeout=None):
        q = Queue()
        self._resultset_bg_thread.queue.put(('SET_' + waiter_type, q))
        try:
            return interruptible_queue_get(q, timeout)
        except (KeyboardInterrupt, Empty):
            self._stream_bg_thread.pause()
            self._resultset_bg_thread.queue.put(('REMOVE_' + waiter_type, q))
            return None
    def show(self):
        tty = TTYSettings()
        q = Queue()
        stdin_monitor = StdinMonitor(q)
        try:
            tty.enter_alt_screen_buffer()
            tty.set_raw_no_echo()
            stdin_monitor.spawn()
            self._stream_bg_thread.start()
            self._resultset_bg_thread.queue.put(('SET_SHOW_WAITER', q))
            keys = []
            while True:
                try:
                    message = q.get(timeout=0.2)
                except Empty:
                    continue
                if message[0] == 'STDIN':
                    c = message[1]
                    if c == b'q':     # stop
                        break
                    elif c == b'A': # up   (we get '\e[A', but '\e' and '[' are ignored)
                        self._resultset_bg_thread.queue.put(('DEC_SHOW_OFFSET',))
                    elif c == b'B': # down
                        self._resultset_bg_thread.queue.put(('INC_SHOW_OFFSET',))
                    elif c == b'5': # up
                        self._resultset_bg_thread.queue.put(('DEC_SHOW_PAGE',))
                    elif c == b'6': # down
                        self._resultset_bg_thread.queue.put(('INC_SHOW_PAGE',))
                    else:
                        continue    # unknown command
                elif message[0] == 'SHOW_VIEW':
                    repr_s = message[1]
                    sys.stdout.write('\x1b[2J' + repr_s)
                    sys.stdout.flush()
        finally:
            self._resultset_bg_thread.queue.put(('REMOVE_SHOW_WAITER',))
            self._stream_bg_thread.pause()
            stdin_monitor.stop()
            tty.restore()
            tty.leave_alt_screen_buffer()
    def _data(self, waiter_type, timeout=None):
        res = self._request(waiter_type, timeout=timeout)
        if res is None:
            return None
        if res['status'] == 'error':
            raise Exception(res['message'])
        for warning in res['warnings']:
            print(warning, file=sys.stderr)
        return res['data']
    def __repr__(self):
        if self._stream_bg_thread.state == 'INIT':
            # try to get a data preview, but give up if no timely response
            self._stream_bg_thread.step()
            self._request('PREVIEW_WAITER', timeout=0.2)
        return self._resultset_bg_thread._current_repr
    def _spawn(self):
        self._resultset_bg_thread.spawn()
        self._stream_bg_thread.spawn()
    def __del__(self):
        self._resultset_bg_thread.stop()
        self._stream_bg_thread.quit()

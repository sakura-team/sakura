from sakura.common.gpu.openglapp import MouseMoveReporting

class OpenglAppBase:
    def __init__ (self, handler):
        self.handler = handler
        self.width   = 100
        self.height  = 100
        self.label   = getattr(handler, "label", 'Unnamed 3D App')
        self.mouse_move_reporting = \
                       getattr(handler, "mouse_move_reporting",
                       MouseMoveReporting.LEFT_CLICKED)
        self.url     = None

    def pack(self):
        return { "mjpeg_url": self.url,
                 "mouse_move_reporting": self.mouse_move_reporting.name }

    def on_resize(self, w, h):
        w, h = int(w), int(h)
        if (w, h) != (self.width, self.height):
            self.width, self.height = w, h
            self.window_resize(w, h)
            self.handler.on_resize(w, h)
            self.notify_change()

    def on_key_press(self, key, x, y):
        self.handler.on_key_press(key, x, y)
        self.notify_change()

    def on_mouse_motion(self, x, y):
        self.handler.on_mouse_motion(x, y)
        self.notify_change()

    def on_mouse_click(self, button, state, x, y):
        self.handler.on_mouse_click(button, state, x, y)
        self.notify_change()

    def display(self):
        self.prepare_display()
        self.handler.display()
        self.release_display()

    def fire_event(self, event_type, *args, **kwargs):
        return getattr(self, event_type)(*args, **kwargs)

    def notify_change(self):
        raise NotImplementedError   # should be implemented in subclass

    def window_resize(self, w, h):
        raise NotImplementedError   # should be implemented in subclass

    def prepare_display(self):
        raise NotImplementedError   # should be implemented in subclass

    def release_display(self):
        raise NotImplementedError   # should be implemented in subclass

    def init(self, w=None, h=None):
        raise NotImplementedError   # should be implemented in subclass

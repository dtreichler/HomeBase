import threading
import queue
from datetime import datetime


class BaseServer(threading.Thread):

    def __init__(self):
        super(BaseServer, self).__init__()
        self.q = queue.Queue()

        self.stop_request = threading.Event()
        self.new_info = threading.Event()

        self.last_info = None
        self.last_time = datetime.fromtimestamp(0)

    def join(self, timeout=None):
        self.stop_request.set()
        super(BaseServer, self).join(timeout)

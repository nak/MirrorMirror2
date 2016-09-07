from datetime import datetime
from pyggi.javascript import  JavascriptClass

from mirror_mirror import BaseUpdater


class Clock(BaseUpdater):

    def __init__(self, webview):
        super(Clock, self).__init__(webview, 30*1000)
        self.html = ""
        self.date_ui = None

    def update(self):
        """
        Display time (update view to do so)
        """
        if self.date_ui is None:
            # must set this here where we are guaranteed page is ready
            # and jquery is loaded
            self.date_ui = self._('#date')
        date = datetime.now()
        self.html = "<p>%s</p><p>%s</p>" % (date.strftime("%I:%M %p"), date.strftime("%A %d"))
        self.date_ui.html(self.html)

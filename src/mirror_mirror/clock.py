from datetime import datetime
from pyggi.javascript import  JavascriptClass

from mirror_mirror import BaseUpdater


class Clock(BaseUpdater):

    def __init__(self, webview):
        super(Clock, self).__init__(webview, 30*1000)

    def update(self):
        """
        Display time (update view to do so)
        """
        date = datetime.now()
        html = "<p>%s</p><p>%s</p>" % (date.strftime("%I:%M %p"), date.strftime("%A %d"))
        self._('#date').html(html)


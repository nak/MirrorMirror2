from datetime import datetime
from pyggi.javascript import  JavascriptClass

class Clock(JavascriptClass):

    def __init__(self, webview):
        self.context = webview.get_main_frame().get_global_context()
        self.webview = webview

    def start(self):
        self.webview.on_view_ready(self._start)

    def _start(self):
        self._ = self.context.get_jsobject("$")
        self.update()
        setInterval = self.context.get_jsobject("window").setInterval
        setInterval(self.update, 30*1000)

    def update(self):
        print "CLOCK UPDATE"
        date = datetime.now()
        html = "<p>%s</p><p>%s</p>" % (date.strftime("%I:%M %p"), date.strftime("%A %d"))
        self._('#date').html(html)


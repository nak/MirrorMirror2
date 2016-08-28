from pyggi.javascript import JavascriptClass


class Calendar(JavascriptClass):

    def __init__(self, webview):
        self.context = webview.get_main_frame().get_global_context()
        self.webview = webview

    def start(self):
        self.webview.on_view_ready(self._start)

    def _start(self):
        self._ = self.context.get_jsobject("$")
        self.update()
        setInterval = self.context.get_jsobject("window").setInterval
        setInterval(self.update, 12*3600*1000)

    def before_show_day(self, date):
        Date = self.context.get_jsobject("Date")
        show = self.context.get_jsobject("show")
        now = " ".join(Date().split(' ')[:3])
        is_today = date.toDateString().startswith(now)
        if is_today:
            css = "now"
        else:
            css = ""
        return [False, css , None]
        #  return False # do not show selectable dates

    def update(self, *args):
        print "CALENDAR UPDATE"
        self._('#calendar').datepicker({
            'inline': True,
            'firstDay': 1,
            'altField': "#actualDate",
            'nextText': '',
            'prevText': '',
            'defaultDate': 0,
            'showOtherMonths': False,
            'beforeShowDay': self.before_show_day,
            'dayNamesMin': ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
            })

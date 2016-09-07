from mirror_mirror import BaseUpdater


class Calendar(BaseUpdater):
    """
    Updates a full calendar (month) view
    """

    def __init__(self, webview):
        super(Calendar, self).__init__(webview,  60*1000)
        self.calendar_ui = None # must set this only when view is ready
        self.Date = self.context.get_jsobject("Date")

    def before_show_day(self, *args):
        """
        callback from calendar that prevents dates as showing as clickable links
        and also highlights current date
        :param date: date to process
        :return: array triplet per javascript spec on (1) if to treat as link, (2) css to be applied, (3) not used here
        """
        if len(args)==0:
            return None
        date = args[0]
        #Date = self.context.get_jsobject("Date")
        now = " ".join(self.Date().split(' ')[:3])
        is_today = date.toDateString().startswith(now)
        css = "now" if is_today else ""
        return [False, css, None]

    def update(self, *args):
        """
        Invoke jquery's datepicker
        """
        if self.calendar_ui is None:
            self.calendar_ui = self._('#calendar')
            self.calendar_ui.datepicker({
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
        self.calendar_ui.datepicker("refresh")

from pyggi.javascript import JavascriptClass
from mirror_mirror import server

class Events(JavascriptClass):

    @classmethod
    def set_view(cls, webview):
        cls.webview = webview
        cls.context = cls.webview.get_main_frame().get_global_context()
        Events.export_class(cls.context, None)

    def __init__(self):
        super(Events, self).__init__(self.context, "Events")
        self.gapi = self.context.get_jsobject("gapi")
        self._ = self.context.get_jsobject("$")
        self.impl = EventsImpl(self.webview, self.context, self.gapi)
        self.impl._checkAuth()

class EventsImpl(object):

    def __init__(self, webview, context, gapi):
        self.webview = webview
        self.context = context
        self.gapi = gapi
        self.immediate = True

    def start(self):
        self.webview.on_view_ready(self._start)

    def _start(self):
        setInterval = self.context.get_jsobject("window").setInterval
        setInterval(self.listUpcomingEvents, 5*60*1000)

    def pocessEvents(self, response):
        events = response.items
        print("%s" % events)

    def listUpcomingEvents(self):
        request = self.gapi.client.calendar.events.list({
             'calendarId': 'primary',
             'timeMin': Date().toISOString(),
             'showDeleted': False,
            'singleEvents': True,
             'maxResults': 10,
             'orderBy': 'startTime'
        })
        request.execute(self.processEvents)

    def _loadCalendarApi(self):
        self.gapi.client.load('calendar', 'v3', self.listUpcomingEvents)

    def _handleResult(self, authResult):
        print "HANDLE RESULT %s" % authResult.error
        self.immediate = False
        if authResult is not None and not authResult.error:
            elem = _("authorize-div")
            elem.style.dispay = 'none';
            self._loadCalendarApi()
            setInterval = self.context.get_jsobject("window").setInterval
            setInterval(self._loadCalendarApi(), 5*60*1000)
        else:
            self._checkAuth()

    def _checkAuth(self):
        client_id = "708470309198-m929jgquangs5shhu35ojs5h7rl9iuml.apps.googleusercontent.com"
        scopes = ["https://www.googleapis.com/auth/calendar.readonly"]
        myauth = self.context.get_jsobject("myauth")
        #self.gapi.auth.authorize
        myauth({'client_id': client_id,
                             'scope': ' '.join(scopes),
                             'immediate': self.immediate},
                            self._handleResult)
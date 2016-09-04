import httplib2
import os
from pkg_resources import resource_filename
from apiclient import discovery
import oauth2client
import glob

from datetime import datetime

from mirror_mirror import BaseUpdater


class Credentials(object):
    """
    A set of credentials that can be used to get a list of a user's calendar events
    """

    SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
    CLIENT_SECRET_FILE = resource_filename("mirror_mirror", os.path.join('resources','events','client.json'))
    APPLICATION_NAME = 'Google Calendar API Python Quickstart'

    def __init__(self, path):
        self.credential_path = path

    def get_credentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        store = oauth2client.file.Storage(self.credential_path)
        credentials = store.get()
        #if not credentials or credentials.invalid:
        #    flow = client.flow_from_clientsecrets(Credentials.CLIENT_SECRET_FILE, Credentials.SCOPES)
        #    flow.user_agent = Credentials.APPLICATION_NAME
        #    credentials = tools.run_flow(flow, store, None)
        return credentials if (credentials and not credentials.invalid) else None

    def list_events(self):
        """
        :returns: a list of events scheduled in the near term for the user
        """
        credentials = self.get_credentials()
        if not credentials:
            return None
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)
        now = datetime.now()
        delta = datetime.utcnow() - now
        now = datetime(now.year, now.month, now.day, 0, 0) + delta
        timeMax = datetime(now.year, now.month, now.day, 23, 59) + delta
        now = now .isoformat() + 'Z' # 'Z' indicates UTC time
        timeMax = timeMax.isoformat() + 'Z'
        calendars = service.calendarList().list().execute()['items']
        calendars = [c['id'] for c in calendars]
        events = []
        for cal in calendars:
            eventsResult = service.events().list(
                calendarId=cal, timeMin=now, timeMax=timeMax, maxResults=10, singleEvents=True,
                orderBy='startTime').execute()
            events += eventsResult.get('items', [])

        return events if events else "No events scheduled for today"


class EventsUpdater(BaseUpdater):

    def __init__(self, webview):
        BaseUpdater.__init__(self, webview, 15*60*1000)
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials', 'mirrormirror2')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        self.credentials = [Credentials(path) for path in glob.glob(os.path.join(credential_dir, "*.json"))]

    def update(self):
        """
        Update the view of a list of upcoming events for the given users (credentials)
        """
        text = "<div>"
        for cred in self.credentials:
            events = cred.list_events()
            if isinstance(events, str):
                text += "<p>%s<p>" % events
            else:
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    text += u"""<p><div style="display:inline;width:20%%">%(start)s</div><br/>
                    <div style="display:inline;width:75%%">[<b>%(user)s</b>] %(summary)s</div></p>""" % {
                        'start': start,
                        'user': event.get('creator',{'displayName': ""})['displayName'],
                        'summary': event.get('summary', "<no summary>")}
        text += "</div>"
        self._('#events').html(text)



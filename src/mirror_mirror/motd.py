import json
from mirror_mirror import BaseUpdater
import requests


class MOTDUpdater(BaseUpdater):

    def __init__(self, webview):
        super(MOTDUpdater, self).__init__(webview, 60*1000)
        self.url = 'http://mirrormirror-141800.appspot.com/?guestbook_name=john_polland;list=1'
        self.greeting = None
        self.html = ""

    def update(self):
        if self.greeting is None:
            self.greeting = self._('#greeting')
        jsn = json.loads(requests.get(self.url).content) or [{'message': 'You look Amazing today!', 'author': None}]
        self.html = "<div>" + \
               "".join(["%(message)s<br/><i style='font-size:50%%'>&nbsp;&nbsp;&nbsp-%(author)s</i><br/>" %
                        {'message': msg['message'],
                         'author': msg.get('author') or 'anonymous'} for msg in jsn]) +\
               "</div>"
        self.greeting.html(self.html)
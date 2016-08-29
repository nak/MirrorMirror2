import json

from mirror_mirror import BaseUpdater

import requests

class MOTDUpdater(BaseUpdater):

    def __init__(self, webview):
        super(MOTDUpdater, self).__init__(webview, 60*1000)

    def update(self):
        url = 'http://mirrormirror-141800.appspot.com/?guestbook_name=john_polland;list=1'
        response = requests.get(url)
        jsn = json.loads(response.content)
        html = "<div>"
        if not jsn:
            jsn = [{'message': 'You look Amazing today!', 'author': None}]
        for msg in jsn:
            if msg.get('author'):
                html += "%(message)s<br/><i style='font-size:50%%'>&nbsp;&nbsp;&nbsp-%(author)s</i><br/>" %{'message': msg['message'],
                                                                                'author': msg['author']}
            else:
                html += "%(message)s<br/>" %{'message': msg['message']}
        html += "</div>"
        self._('#greeting').html(html)
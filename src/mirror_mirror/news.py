import json

import requests
from mirror_mirror import BaseUpdater

class NewsUpdater(BaseUpdater):
    """
    Updates a view related to latest news
    """

    api_key = 'cc0ff410c2054f5aadd2a5b1a6e14ba0'

    def __init__(self, webview):
        super(NewsUpdater, self).__init__(webview, 12*60*60*1000)


    @classmethod
    def get_resource(cls, section, limit=5):
        return 'https://api.nytimes.com/svc/news/v3/content/all/%(section)s.json?api-key=%(api_key)s,limit=%(limit)s' %\
               {'section': section,
                'api_key': cls.api_key,
                'limit': limit}

    def update(self):
        """
        Update the view of the latest news headlines
        """
        text=u"<div>"
        for section in ['technology', 'u.s.', 'world']:
            resource_url = self.get_resource(section)
            response = requests.get(resource_url)
            results = json.loads(response.content)["results"]
            for result in results[:1]:
                abstract = result['abstract'].encode("ascii",'ignore')
                text += u"<p><b>[%(section)s]</b> %(abstract)s...</p>" % {'section': result['section'],
                                                                       'abstract': abstract[:min(len(abstract),100)]}
        text += u"</div>"
        self._('#news').html(text)

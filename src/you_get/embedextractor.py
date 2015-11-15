from importlib import import_module
from .common import alias

class EmbedExtractor():
    """
    this class is to help video embed site to handle
    video from other site.
    we just need to know the source site name, and video ID
    that's enough.
    with site name and VID, develop can easily to find out the real URL

    because embed site don't have video info, so they don't need stream_info.
    """

    def __init__(self, *args):
        self.video_info = []
        self.video_url = []
        self.title = None
        if args:
            self.url = args[0]

    def prepare(self, **kwargs):
        """
        this API is to do real job to get site and VID
        sometimes title
        MUST override!!
        """
        pass

    def download_by_url(self, url, param, **kwargs):
        self.param = param
        self.url = url
        self.video_info = []
        self.video_url = []
        self.prepare(**kwargs)

        if not self.video_info and not self.video_url:
            raise NotImplementedError(self.url + " is not supported")

        if self.video_info:
            for v in self.video_info:
                site, vid = v
                if site in alias.keys():
                    site = alias[site]
                s = import_module('.'.join(['you_get','extractors',site]))
                s.site.download_by_vid(vid, self.param, title=self.title, **kwargs)

        if self.video_url:
            for v in self.video_url:
                site, url = v
                if site in alias.keys():
                    site = alias[site]
                s = import_module('.'.join(['you_get','extractors',site]))
                s.site.download_by_url(url, self.param, **kwargs)

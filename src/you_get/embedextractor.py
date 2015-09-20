from importlib import import_module

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

    def download(self, url, **kwargs):
        self.url = url

        self.prepare(**kwargs)

        if not self.video_info:
            raise NotImplementedError(self.url + "is not supported")

        for v in self.video_info:
            site, vid = v
            #enhancemant needed, just know upstream has related patch, and wait a few days
            s = import_module('.'.join(['you_get','extractors',site]))
            s.site.download_by_vid(vid, title=self.title, **kwargs)

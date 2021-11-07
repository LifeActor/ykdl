from logging import getLogger


class VideoExtractor():
    def __init__(self):
        self.logger = getLogger(self.name)
        self.url = None
        self.vid = None

    def parser(self, url):
        self.__init__()
        if isinstance(url, str) and url.startswith('http'):
            self.url = url
            if self.list_only():
                return self.parser_list(url)
        else:
            self.vid= url

        info = self.prepare()
        return info

    def parser_list(self, url):
        self.url = url
        video_list = self.prepare_list()
        if not video_list:
            raise NotImplementedError(
                    'playlist not support for {self.name} with url: {self.url}'
                    .format(**vars()))
        for video in video_list:
            yield self.parser(video)

    def __getattr__(self, attr):
        return None

    def prepare(self):
        pass

    def prepare_list(self):
        pass

    def list_only(self):
        '''
        this API is to check if only the list informations is included
        if true, go to parser list mode
        MUST override!!
        '''
        pass

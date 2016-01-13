from ..embedextractor import EmbedExtractor
from ..common import playlist_not_supported

class Netease(EmbedExtractor):
    def prepare(self, **kwargs):
        assert self.url

        if self.url.startswith("http://cc"):
            self.video_url.append(("neteaselive", self.url))
        elif self.url.startswith("http://music"):
            self.video_url.append(("neteasemusic", self.url))
        else:
            self.video_url.append(("neteasevideo", self.url))

site = Netease()
download = site.download_by_url
download_playlist = playlist_not_supported('163')

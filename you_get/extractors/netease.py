from ..embedextractor import EmbedExtractor

class Netease(EmbedExtractor):
    def prepare(self):

        if self.url.startswith("http://cc"):
            self.video_info.append(("neteaselive", self.url))
        elif self.url.startswith("http://music"):
            self.video_info.append(("neteasemusic", self.url))
        else:
            self.video_info.append(("neteasevideo", self.url))

site = Netease()

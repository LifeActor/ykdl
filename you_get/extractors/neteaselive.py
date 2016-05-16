from ..util.html import get_content
from ..util.match import match1
from ..extractor import VideoExtractor
import json

class NeteaseLive(VideoExtractor):
    name = "网易直播 (163)"

    def prepare(self):

        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, "anchorCcId : \'([^\']+)")
            self.title = match1(html, "<title>([^<]+)")
        else:
            self.title = self.name + str(self.vid)

        info = json.loads(get_content("http://cgi.v.cc.163.com/video_play_url/{}".format(self.vid)))

        self.stream_types.append("current")
        self.streams["current"] = {'container': 'flv', 'video_profile': "current", 'src' : [info["videourl"]], 'size': 0}

site = NeteaseLive()

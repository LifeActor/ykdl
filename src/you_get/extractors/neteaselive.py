from ..util.html import get_content
from ..util.match import match1
from ..extractor import VideoExtractor
from ..common import playlist_not_supported
import json

class NeteaseLive(VideoExtractor):
    name = "网易直播 (163)"

    def prepare(self, **kwargs):
        assert self.url or self.vid

        if not self.vid:
            html = get_content(self.url)
            self.vid = match1(html, "anchorCcId : \'([^\']+)")

        info = json.loads(get_content("http://cgi.v.cc.163.com/video_play_url/{}".format(self.vid)))

        self.stream_types.append("current")
        self.streams["current"] = {'container': 'flv', 'video_profile': "current", 'src' : [info["videourl"]], 'size': 0}

site = NeteaseLive()
download = site.download_by_url

# You-Get

[You-Get](http://www.soimort.org/ykdl) is a video downloader for [YouTube](http://www.youtube.com), [Youku](http://www.youku.com), [niconico](http://www.nicovideo.jp) and a few other sites.

`ykdl` is a command-line program, written completely in Python 3. Its prospective users are those who prefer CLI over GUI. With `ykdl`, downloading a video is just one command away:

    $ ykdl http://youtu.be/sGwy8DsUJ4M

这只是一个[You-Get](http://www.soimort.org/ykdl)的代码美化版本

请参考[上游](http://www.soimort.org/ykdl)以便获得更多信息

##正题
### 为什么会有这个Fork
* 因为原代码写得比较散，自己为了练手，决定美化代码
* 接收一些[Upstream](http://www.soimort.org/ykdl)暂时没有被合并的代码，以cherry-pick方式

### 这个Fork的目标是什么
* 用VideoExctrator重写，目前基本完工，除了几个目前已经坏掉的站点外。
* 更优美的支持音乐站点
* 更佳的公共代码结构，以方便维护和阅读
* 统一的视频格式代码（--format的参数目前是不确定的）
* 外部工具的支持

### 和上游的区别有哪些
* 代码更结构化，未来会更结构化
* 去掉了很多死站，大多是外国网站
* 对腾讯视频, 斗鱼, 优酷的支持比上游好一些
* 支持湖南卫视，火猫TV

### 贡献代码
* 定期从上游cherry-pick patch，所以只需贡献给上游即可
* 不定期从上游的活跃fork cherry-pick重要patch
* 直接提pull request


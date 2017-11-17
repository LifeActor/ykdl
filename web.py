from flask import Flask
from flask import request
app = Flask(__name__)


from ykdl.common import url_to_module
from ykdl.util.wrap import launch_player
from ykdl.version import __version__

@app.route('/play', methods=['PUT', 'GET'])
def play():
    if request.method == 'PUT':
        url = request.form['url']
        m,u = url_to_module(url)
        try:
            info = m.parser(u)
        except AssertionError as e: 
            return str(e)
        player_args = info.extra
        player_args['title'] = info.title
        urls = info.streams[info.stream_types[0]]['src']
        launch_player("mpv", urls, **player_args)
        return "OK"
    else:
        return "curl -X put --data-urlencode \"url=<URL>\" http://IP:5000/play"
     
@app.route('/version')
def version():
    return __version__

if __name__ == '__main__':
    app.run(host='0.0.0.0')

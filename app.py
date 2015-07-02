# -*- coding: utf8 -*-
from gevent import monkey;
monkey.patch_all()

import gevent
from flask import Flask, render_template, request
from flask.ext.socketio import SocketIO, emit
from twython import TwythonStreamer

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

from config import CONF


class TwitterStreamer(TwythonStreamer):
    def __init__(self, *args, **kwargs):
        TwythonStreamer.__init__(self, *args, **kwargs)
        print("Initialized TwitterStreamer.")
        self.queue = gevent.queue.Queue()

    def on_success(self, data):
        self.queue.put_nowait(data)
        if self.queue.qsize() > 10000:
            self.queue.get()

    def on_error(self, status_code, data):
        print status_code, data, "TwitterStreamer stopped because of an error!"
        self.disconnect()


class TwitterWatchDog:
    def __init__(self):
        self.init()

    def init(self):
        self.streamer = TwitterStreamer(CONF['APP_KEY'], CONF['APP_SECRET'], CONF['OAUTH_TOKEN'], CONF['OAUTH_TOKEN_SECRET'])
        self.green = gevent.spawn(self.streamer.statuses.filter, track="samsung")

    def check_alive(self):
        if self.green.dead:
            # stop everything
            self.streamer.disconnect()
            self.green.kill()
            # then reload
            self.init()


dog = TwitterWatchDog()


@app.route('/')
def index():
    dog.check_alive()
    return render_template('index.html')


@socketio.on('connect', namespace='/tweets')
def tweets_connect():
    dog.check_alive()
    uid = request.namespace.socket.sessid
    print('Client %s connected' % uid)
    while True:
        try:
            tweet = dog.streamer.queue.get(timeout=5)
        except gevent.queue.Empty:
            dog.check_alive()
        else:
            emit('tweet', tweet, broadcast=True)


@socketio.on('disconnect', namespace='/tweets')
def tweets_disconnect():
    dog.check_alive()
    uid = request.namespace.socket.sessid
    print('Client %s disconnected' % uid)


if __name__ == '__main__':
    try:
        socketio.run(app, port=5000, host="0.0.0.0")
    except KeyboardInterrupt:
        pass

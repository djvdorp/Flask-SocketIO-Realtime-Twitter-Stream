# Flask-SocketIO Realtime Twitter Stream

## Installation
Prepare the environment:

```
$ virtualenv venv
$ source venv/bin/activate
$ (venv) pip install -r requirements.txt
$ (venv) cp config.dist.py config.py
```

Then edit config.py with your Twitter credentials and search keyword(s) - comma separated - and run:

```
$ (venv) python app.py
```

## Credits
Based on the idea of [mattgu74/TwitterHeatMap](https://github.com/mattgu74/TwitterHeatMap) and the example from [miguelgrinberg/Flask-SocketIO](https://github.com/miguelgrinberg/Flask-SocketIO).
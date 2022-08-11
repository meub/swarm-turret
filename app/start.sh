echo Starting camera server and websocket server.
gunicorn --reload --timeout 6000 -w 1 --bind 0.0.0.0:6001 camera:app --daemon
gunicorn --reload -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 --bind 0.0.0.0:5000 main:app --daemon
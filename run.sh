#!/usr/bin/env bash

gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w "$1" --log-level=debug \
  --access-logfile - --error-logfile - "cerf7:create_app()"

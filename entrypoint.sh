#! /bin/sh
set -e

# wait PostgreSQL to start
sleep 10

case $1 in
    app)
        flask db upgrade
        gunicorn -w 4 -t 3600 -b 0.0.0.0:5000 --log-level=$GUNICORN_LOGLEVEL api_collection:app
        ;;
    celery)
        celery -A api_collection.celery worker -c $CELERY_CONCURRENCY
        ;;
    flower)
        celery -A api_collection.celery flower --port=5555 --url_prefix=flower
        ;;
    socketio)
        python run_socketio.py 2>&1
        ;;
    *)
        $@
esac

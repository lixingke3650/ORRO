# !/bin/sh

GUNICORN=/usr/local/bin/gunicorn
ROOT=/var/web/orro

APP=Orro_R:app

cd $ROOT
exec $GUNICORN -c $ROOT/gunicorn.conf.py $APP

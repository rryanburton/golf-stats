#!/bin/sh
set -e
#set -xv

if [ -z "$WORKSPACE" ]; then
    INSTALL_DIR=`pwd`
else
    INSTALL_DIR=$WORKSPACE
fi

if [ -z "$BUILD_ID" ]; then
    BUILD_ID='DEV'
fi


PROJECT_NAME=golfstats
PROJECT_SHORT_NAME=golfstats
ROOT=/opt/$PROJECT_SHORT_NAME
VENV=$ROOT/venv
VPYTHON="$VENV/bin/python"
VPIP=$VENV/bin/pip
VFAB=$VENV/bin/fab
FABFILE=$INSTALL_DIR/src/fabfile.py
DEPLOY=$ROOT/deployment-temp
DEPLOYMENTS=$ROOT/deployments
APP_DIR=$ROOT/app

MANAGE="$VPYTHON $INSTALL_DIR/src/manage.py"
BACKUP_DIR=$ROOT/backups


PACKAGE_NAME=release-$BUILD_ID


case "$1" in

manage)
    _manage $2
    ;;

backup-database)
    DATE=`/bin/date '+%Y_%m_%d_%H-%M'`
    mkdir -p $BACKUP_DIR/db
    DUMPFILE=$BACKUP_DIR/db/$PROJECT_NAME-$DATE.backup
    pg_dump --host=PC004 --username=$PROJECT_NAME --verbose --format=custom --compress=9 --file=$DUMPFILE $PROJECT_NAME-production
    DUMP_RESULT=$?

    if [ $DUMP_RESULT -ne 0 ] ; then
    {
      echo "Database dump FAILED"
    }
    else
    {
      echo "Database dump Succeeded"
    }
    fi
    ;;

restore-database)
    latest_name=`ls -t -r $BACKUP_DIR/db/ | tail -n 1`
    echo "File name: ${latest_name}"
    createdb --host=PC010 --username=$PROJECT_NAME --echo --owner=$PROJECT_NAME ${latest_name}
    pg_restore --host=PC010 --username=$PROJECT_NAME --jobs 8 --verbose --exit-on-error --format=custom --dbname ${latest_name} $BACKUP_DIR/db/${latest_name}
    ;;

install-build)
    # Run as a developer
    sudo apt-get -y install python g++ make checkinstall
    cd ~/.
    mkdir -p src/nodejs
    cd src/nodejs
    wget -N http://nodejs.org/dist/node-latest.tar.gz
    tar xzvf node-latest.tar.gz
    cd node-v*
    ./configure
    make
    sudo make install

    sudo npm -g install yuglify less
    ;;

install-memcached)
    # Run as a root
    apt-get install memcached
    ;;

install-nginx) echo 'Installing nginx'
    # run as root

    wget --quiet -O - http://nginx.org/packages/keys/nginx_signing.key | apt-key add -
    ln -nsf $APP_DIR/configuration/nginx/nginx.list /etc/apt/sources.list.d/nginx.list
    apt-get update
    apt-get -y install nginx

    ln -nsf $APP_DIR/configuration/nginx/$PROJECT_NAME.conf /etc/nginx/conf.d/$PROJECT_NAME.conf
    ln -nsf $APP_DIR/configuration/nginx/$PROJECT_NAME-dev.upstream.conf /etc/nginx/conf.d/$PROJECT_NAME-dev.upstream.conf
    ln -nsf $APP_DIR/configuration/nginx/$PROJECT_NAME-production.upstream.conf /etc/nginx/conf.d/$PROJECT_NAME-production.upstream.conf
    service nginx restart
    ;;

install-uwsgi) echo 'Installing uwsgi'
    # run as root
    ln -nsf $APP_DIR/configuration/supervisord/$PROJECT_NAME-uwsgi.conf /etc/supervisor/conf.d/$PROJECT_NAME-uwsgi.conf
    ln -nsf $APP_DIR/configuration/logrotate/$PROJECT_NAME /etc/logrotate.d/$PROJECT_NAME
    service supervisor restart
    supervisorctl update
    supervisorctl restart all
    ;;


gen-icons)
    echo $PROJECT_NAME.svg
    inkscape --export-png=src/static/ico/apple-touch-icon-57-precomposed.png --export-width=57 --export-height=57 $PROJECT_NAME.svg
    inkscape --export-png=src/static/ico/apple-touch-icon-72-precomposed.png --export-width=72 --export-height=73 $PROJECT_NAME.svg
    inkscape --export-png=src/static/ico/apple-touch-icon-114-precomposed.png --export-width=114 --export-height=114 $PROJECT_NAME.svg
    inkscape --export-png=src/static/ico/apple-touch-icon-144-precomposed.png --export-width=144 --export-height=144 $PROJECT_NAME.svg

    inkscape --export-png=src/static/ico/favicon_32.png --export-width=32 --export-height=32 $PROJECT_NAME.svg
    inkscape --export-png=src/static/ico/favicon_64.png --export-width=64 --export-height=64 $PROJECT_NAME.svg

    inkscape --export-png=src/static/ico/tileimage_144.png --export-width=144 --export-height=144 $PROJECT_NAME.svg

    inkscape --export-png=src/static/favicon.png --export-width=16 --export-height=16 $PROJECT_NAME.svg

    #sudo apt-get install icoutils
    icotool -o src/static/favicon.ico -c src/static/favicon.png

    inkscape --export-png=src/static/logo.png --export-width=32 --export-height=32 $PROJECT_NAME.svg
    ;;

bootstrap)

    virtualenv $VENV
    $VPIP install fabric
    ;;

bare-metal-init)
    $VFAB -f $FABFILE -H $2 bare-metal-init
    ;;

build)
    echo '**** Updating Virtual Environment ****'
    $VPIP install -r $INSTALL_DIR/requirements.txt


    echo '**** Collecting Static ****'
    $MANAGE collectstatic --noinput

    echo '**** Deleting Compiled Files ****'
    find $INSTALL_DIR -name "*.pyc" -exec rm -f {} \;
    ;;

deploy)
    DEPLOY_HOST=$2
    SETTINGS=$3
    $VFAB -f $FABFILE -H $PROJECT_NAME@$DEPLOY_HOST deploy:package_name=$PACKAGE_NAME,settings=$SETTINGS,build_id=$BUILD_ID
    ;;

restart_supervisor)
    DEPLOY_HOST=$2
    PROGRAM=$3
    $VFAB -f $FABFILE -H $PROJECT_NAME@$DEPLOY_HOST restart_supervisor:program=$PROGRAM
    ;;


*) echo 'No option set'
    exit 0;
    ;;

esac

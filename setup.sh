#!/bin/bash

PROJECT_DIR=~/SuMeMainTest
VIRTUALENV_NAME=SuMeMainEnv

echo "Install basic initial packages required............."
sudo apt-get update
sudo apt-get install vim python3 python3-dev nginx postgresql postgresql-contrib

echo "Setup Flask in a virtual env....................."
mkdir $PROJECT_DIR
cd $PROJECT_DIR
mkdir app
virtualenv $VIRTUALENV_NAME
source $VIRTUALENV_NAME/bin/activate
pip install uwsgi flask
deactivate

echo "Configure uwsgi...................."
cat << 'EOF' > $PROJECT_DIR/app/uwsgi.ini
[uwsgi]

module = wsgi

master = true
processes = 5

socket = /tmp/sume_internal.sock
chmod-socket = 660
uid = www-data
gid = www-data
vacuum = true

die-on-term = true
EOF

echo "Setup nginx to proxy requests........."
sudo touch /etc/nginx/sites-available/SuMeNginx.conf
sudo tee /etc/nginx/sites-available/SuMeNginx.conf << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    location / {
        include uwsgi_params;
        uwsgi_pass unix:/tmp/sume_internal.sock;
    }
}
EOF

sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/SuMeNginx.conf /etc/nginx/sites-enabled
sudo service nginx restart

cd $PROJECT_DIR/app
cat << 'EOF' > wsgi.py
from sume_main import application

if __name__ == "__main__":
    application.run(host='0.0.0.0')
EOF

cat << 'EOF' > sume_main.py
from flask import Flask

application = Flask(__name__)

@application.route('/')
def hello():
    return "Hello, World!"

if __name__ == "__main__":
    application.run(host='0.0.0.0')
EOF

touch __init__.py

echo "Bring up the SuMe application......"
sudo ../$VIRTUALENV_NAME/bin/uwsgi -i uwsgi.ini &
echo "===================================================="
echo "If by chance everything went fine, you will see Hello world message when you connect to current IP via a decent browser."

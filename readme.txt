sudo dnf install httpd -y
sudo systemctl enable httpd
sudo systemctl start httpd
----------------------------------------------
sudo dnf install mariadb-server mariadb -y
sudo systemctl enable mariadb
sudo systemctl start mariadb

# تنظیم رمز عبور MariaDB
sudo mysql_secure_installation
----------------------------------------------
sudo dnf install python3 python3-pip -y
sudo yum install mod_ssl
----------------------------------------------
pip3 install flask pymysql
pip3 install flask_sqlalchemy flask_login requests requests-oauthlib flask-migrate flask-sqlalchemy
pip install bcrypt Flask-WTF python-dotenv email-validator



-----------------------------
sudo mkdir -p /var/www/wlcomco
sudo chmod -R 755 /var/www/wlcomco
----------------------------------------
sudo nano /var/www/wlcomco/wlcomco.wsgi


import sys
sys.path.insert(0, '/var/www/wlcomco')

from app import app as application
-----------------------------------------
sudo nano /var/www/wlcomco/app.py

from flask import Flask
import pymysql

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World! Flask is running with MariaDB and Apache on wlcomco."

if __name__ == '__main__':
    app.run()
-----------------------------------------------
sudo dnf install mod_wsgi -y
---------------------------------
sudo nano /etc/httpd/conf.d/wlcomco.conf

<VirtualHost *:80>
    ServerName your_domain_or_IP
    DocumentRoot /var/www/wlcomco

    WSGIScriptAlias / /var/www/wlcomco/wlcomco.wsgi

    <Directory /var/www/wlcomco>
        Require all granted
    </Directory>

    Alias /static /var/www/wlcomco/static
    <Directory /var/www/wlcomco/static/>
        Require all granted
    </Directory>
</VirtualHost>
------------------------------------------------
sudo chown -R apache:apache /var/www/wlcomco
---------------------------------------------------
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
--------------------------------------------------
pip3 install mysql-connector-python
------------------------------------------------
sudo setsebool -P httpd_can_network_connect 1
-------------------------------------------------
sudo mysql -u root -p

CREATE DATABASE wlcomco_db;
CREATE USER 'wlcomco_user'@'localhost' IDENTIFIED BY '4314314522P@ss';
GRANT ALL PRIVILEGES ON wlcomco_db.* TO 'wlcomco_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
--------------------------------------------------
sudo systemctl restart httpd
--------------------------------------------------



---------------------
for update DATABASE
---------------------
flask --app app:create_app db init
flask db migrate -m "Description"
flask db upgrade


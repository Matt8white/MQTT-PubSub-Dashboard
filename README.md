# MQTT-PubSub Dashboard
Simple publisher-subscriber in python with the purpose of sending a machine 
diagnostic remotely to a server which will store all the collected information 
in Graphite, used to track the performance of the sender. The information can be 
displayed in a dashboard using Grafana.

## Installation

### Linux

Server side, we should update our local package index and install all the system 
packages required for working to graphite.
```
sudo apt update 
sudo apt upgrade
sudo apt install build-essential graphite-web graphite-carbon python-dev apache2 libapache2-mod-wsgi libpq-dev python-psycopg2
```
#### Configure Carbon
If you want to change the way whisper stores the data you can modify the file 
`/etc/carbon/storage-schemas.conf`:
```
[carbon]
pattern = ^carbon\.
retentions = 60:90d

[default_1min_for_1day]
pattern = .*
retentions = 60s:1d
```
by adding for example the section `[test]`
```
[test]
pattern = ^test\.
retentions = 5s:3h,1m:1d
```
In this example, for metrics starting with with "test", it sets the retentions 
time in order to save data every 5 seconds for 3 hours, and a separate set of 
data from that aggregated sample every 1 minute for 1 day.

You also need to copy the default aggregation configuration to `/etc/carbon` in 
order to make your own settings:
```
sudo cp /usr/share/doc/graphite-carbon/examples/storage-aggregation.conf.example /etc/carbon/storage-aggregation.conf
```
Lastly, you need start the carbon-cache service:
```
sudo service carbon-cache start
```

#### Install and configure PostgreSQL
Install PostgreSQL for the graphite-web application:
```
sudo apt-get install postgresql
```
Then create a superuser and a database:
```
sudo -u postgres psql
CREATE USER graphite WITH PASSWORD 'password';
CREATE DATABASE graphite WITH OWNER graphite;
\q
```
#### Configure Graphite

Update Graphite’s databases dictionary definition with the settings for the 
PostgreSQL database created earlier by modifying `/etc/graphite/local_settings.py:
```
DATABASES = {
'default': {
    'NAME': 'graphite',
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'USER': 'graphite',
    'PASSWORD': 'graphiteuserpassword',
    'HOST': '127.0.0.1',
    'PORT': ''
    }
}

USE_REMOTE_USER_AUTHENTICATION = True
TIME_ZONE = 'Your/Timezone'
SECRET_KEY = 'somelonganduniquesecretstring'
````
Initlialize the database:
```
sudo graphite-manage syncdb
```
#### Configure Apache for Graphite
Copy Graphite’s Apache config template into Apache’s sites-available directory:
```
sudo cp /usr/share/graphite-web/apache2-graphite.conf /etc/apache2/sites-available
```
Disable the default Apache site to avoid conflicts:

```
sudo a2dissite 000-default
```

Enable Graphite’s virtual site:
```
sudo a2ensite apache2-graphite`
```
Reload Apache to apply the changes:
```
sudo service apache2 reload
```
Now you can access Graphite by typing in your browser `http://localhost:80`.

We don't want graphite to be reachable from the open world so make sure your 
firewall block any incoming connection on port 80.

#### Install Grafana

Add Grafana’s repository to sources.list:
```
echo 'deb https://packagecloud.io/grafana/stable/debian/ wheezy main' |  sudo tee -a /etc/apt/sources.list

```
Add the Package Cloud key to install signed packages:
```
curl https://packagecloud.io/gpg.key | sudo apt-key add -
```

Update apt and install Grafana:

```
sudo apt update && sudo apt install grafana
```

Configure Grafana to use the PostgreSQL database created earlier, set the domain 
and root_url, and set a strong admin password and secret key (You may also want 
to disable the possibility for any user to create an account):

in `/etc/grafana/grafana.ini`
```
[database]
# Either "mysql", "postgres" or "sqlite3", it's your choice
type = postgres
host = 127.0.0.1:5432
name = grafana
user = graphite
password = graphiteuserpassword

[server]
protocol = http
http_addr = 127.0.0.1
http_port = 3000
domain = example.com
enforce_domain = true
root_url = %(protocol)s://%(domain)s/

[security]
admin_user = admin
admin_password = SecureAdminPass
secret_key = somelongrandomstringkey

[users]
# disable user signup / registration
allow_sign_up = false
```
Start grafana server: 
```
sudo service grafana-server start
```
Grafana needs to be reachable from the outside world so make sure port 3000 is 
open on your firewall.

Now you can log in with your admin account on Grafana and add your data source 
previously set up. (This can be easily made following the Grafana GUI).

#### Install MQTT broker

Install the mosquitto broker which will run on the server:
```
sudo apt install mosquitto mosquitto-clients
```

Configure Mosquitto to use passwords. Mosquitto includes a utility to generate a 
special password file called mosquitto_passwd. This command will prompt you to 
enter a password for the specified username, and place the results in 
`/etc/mosquitto/passwd`.
```
sudo mosquitto_passwd -c /etc/mosquitto/passwd test
```
Now we'll open up a new configuration file for Mosquitto and tell it to use this
password file to require logins for all connections:

```
sudo nano /etc/mosquitto/conf.d/default.conf
```

This should open an empty file. Paste in the following:

```
allow_anonymous false
password_file /etc/mosquitto/passwd
```
`allow_anonymous` false will disable all non-authenticated connections, and the 
`password_file` line tells Mosquitto where to look for user and password 
information. Save and exit the file.

Now you need to restart Mosquitto.
```
sudo systemctl restart mosquitto
```

Last thing to do is to run subscriber.py on the server, which will listen to 
various topics (which can be modified) and store them on the graphite database
previously set up:

Usage
```
python subscriber.py --mqtt_usr <your username> --mqtt_pwd <your password> --mqtt_address <your broker address>
```

And now target machines can run publisher.py which will collect and send 
performance metrics and send them to the selected broker:

Usage
```
python publisher.py --mqtt_usr <your username> --mqtt_pwd <your password> --mqtt_address <your broker address>
```
This documentation was created following these guides:
- [Link 1 (only graphite)](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-graphite-on-an-ubuntu-14-04-server)
- [Link 2](https://www.linode.com/docs/uptime/monitoring/deploy-graphite-with-grafana-on-ubuntu-14-04)
- [Link 3](https://community.rackspace.com/products/f/25/t/6800)
- [Link 4](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-the-mosquitto-mqtt-messaging-broker-on-ubuntu-16-04)

### macOS

First of all you need to install an MQTT message broker
```
brew install mosquitto
```

Then you need to install a python module which will manage the MQTT client, for 
example paho mqtt:
```
pip install paho-mqtt
```
Then you just need to run `python subscriber.py` on the server and 
`python publisher.py` on the sender machine. (Arguments may be needed, see code for details)


In order to correctly store and plot the information sent by the publisher you 
need to install on the server the following:

#### Dependencies
##### Install Cairo and related
For macOS
```
brew install cairo
brew install py2cairo
```
##### Install Django
```
pip install Django==1.5
pip install django-tagging
```

#### Graphite
```
pip install carbon
pip install whisper
pip install graphite-web
pip install Twisted==11.1.0 

chown -R <your username>:staff /opt/graphite
```

##### Configuration
Create in `/opt/graphite/conf` configuration files for carbon and for the 
storage schema of the DB. You can use the default ones by using this:
```
cp /opt/graphite/conf/carbon.conf{.example,}
cp /opt/graphite/conf/storage-schemas.conf{.example,}
```
You can also modify them in order to change things like the frequency at which 
the data is stored in the DB

##### Create default DB

```
cd /opt/graphite/webapp/graphite

# Modify this file to change database backend (default is sqlite).
cp local_settings.py{.example,}

# Initialize database
python manage.py syncdb
```

##### Start Carbon and Graphite

```
python /opt/graphite/bin/carbon-cache.py start

# You may need to add to the env paths the folder
# export PYTHONPATH="/opt/graphite/webapp"
python /opt/graphite/bin/run-graphite-devel-server.py /opt/graphite
```

Go to `http://localhost:8080` to see if Graphite is properly running

### Grafana
Refer to [download guide](https://grafana.com/grafana/download)

##### Start server
```
grafana-server -homepath /usr/local/share/grafana/
```
With Grafana server up and running you just need to access 
`http://localhost:3000` and
- Add Graphite as data source
- Create your custom dashboards

For grafana usage without using the GUI refer to these links:
- [grafana-dashboard-builder](https://github.com/jakubplichta/grafana-dashboard-builder)
- [grafcli](https://github.com/m110/grafcli)
- [adding datasource](https://github.com/grafana/grafana/issues/1789)

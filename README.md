# MQTT-PubSub Dashboard
Simple publisher-subscriber in python with the purpose of sending a machine diagnostic 
remotely to a server which will store all the collected information in Graphite,
used to track the performance of the sender. The information can be displayed in
a dashboard using Grafana.

## Installation

For Linux

Refer to these links:
- [Link 1 (only graphite)](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-graphite-on-an-ubuntu-14-04-server)
- [Link 2](https://www.linode.com/docs/uptime/monitoring/deploy-graphite-with-grafana-on-ubuntu-14-04)
- [Link 3](https://community.rackspace.com/products/f/25/t/6800)

For macOS

First of all you need to install an MQTT message broker
```
brew install mosquitto
```
In order to enable password protection see [this link](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-the-mosquitto-mqtt-messaging-broker-on-debian-8)

Then you need to install a python module which will manage the MQTT client, for 
example paho mqtt:
```
pip install paho-mqtt
```
Then you just need to run `python subscriber.py` on the server and 
`python publisher.py` on the sender machine. (Arguments may be needed, see code for details)


In order to correctly store and plot the information sent by the publisher you 
need to install on the server the following:

### Dependencies
#### Install Cairo and related
For macOS
```
brew install cairo
brew install py2cairo
```
#### Install Django
```
pip install Django==1.5
pip install django-tagging
```

### Graphite
```
pip install carbon
pip install whisper
pip install graphite-web
pip install Twisted==11.1.0 

chown -R <your username>:staff /opt/graphite
```

#### Configuration
Create in `/opt/graphite/conf` configuration files for carbon and for the 
storage schema of the DB. You can use the default ones by using this:
```
cp /opt/graphite/conf/carbon.conf{.example,}
cp /opt/graphite/conf/storage-schemas.conf{.example,}
```
You can also modify them in order to change things like the frequency at which 
the data is stored in the DB

#### Create default DB

```
cd /opt/graphite/webapp/graphite

# Modify this file to change database backend (default is sqlite).
cp local_settings.py{.example,}

# Initialize database
python manage.py syncdb
```

#### Start Carbon and Graphite

```
python /opt/graphite/bin/carbon-cache.py start

# You may need to add to the env paths the folder
# export PYTHONPATH="/opt/graphite/webapp"
python /opt/graphite/bin/run-graphite-devel-server.py /opt/graphite
```

Go to `http://localhost:8080` to see if Graphite is properly running

### Grafana
Refer to [download guide](https://grafana.com/grafana/download)

#### Start server
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

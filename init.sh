#!/bin/sh

python /Users/mattwhite/anaconda/bin/carbon-cache.py start
export PYTHONPATH="/Users/mattwhite/anaconda/webapp"
python run-graphite-devel-server.py /Users/mattwhite/anaconda/webapp/graphite
grafana-server -homepath /usr/local/share/grafana/

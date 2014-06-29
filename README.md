# ElasticMonitor - Stats Worker

A CPU, RAM, and Disk Utilisation statistics collector that pushes to an ElasticSearch node/endpoint. It uses the official ElasticSearch Python library.

Ideally this will become a part of a larger project, but for now, this is it.

# Installation & Use

First, clone the repository to a local directory on your server(s). Now use Python 'virtualenv' to create a virtual environment to run the worker from. Once you have this, you can use 'pip install -r requirements.txt' (using the pip installed inside the virtualenv) to download and install all the required packages. These packages will be installed into the local virtualenv.

Once you have a virtualenv installed and setup with the required modules, simply edit 'config.yaml' to match the location and configuration of your ElasticSearch cluster/node/endpoint and then run 'python run.py'. This will collect the stats and push to the configured ES endpoint.

## Cronjob

To keep pushing the system stats into ElasticSearch on a regular basis, like a monitoring system would, consider setting up a cronjob to execute the Python script (from within the virtualenv, remember) on a fixed schedule. You can replicate, roughly, a monitoring system's setup by running the script once every 3-5 minutes. 

# Possible Uses

This is a simple idea, and was written in a few hours to help out a fellow ElasticSearch user. However it may become something more serious in time. At this point in time, it's a fun little utility that demonstrates two awesome libraries: psutil and elasticsearch.

In the long run, this may become something a bit more serious that embodies an entire monitoring platform for Linux systems. This would require some heavy architecting, but it's possible and would provide great flexbility and scaling, thanks to ElasticSearch.

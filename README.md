# openwifimap-api (Python)
OpenWiFiMap is a database and map for free network WiFi routers (freifunk and others, too!).

This is the database/backend part of the openwifimap.
Make sure to also take a look at its web frontend, the [openwifimap HTML5 app](https://github.com/freifunk/openwifimap-html5).

The original backend was written in Javascript using CouchDB.
Since maintaining that was problematic, it was rewritten in 2020/2021 to use Python/FastAPI/PostgreSQL.

# API
See the Swagger API docs at `/docs` on the running backend (at [api.openwifimap.net/docs](https://api.openwifimap.net/docs), for example).

The somewhat more verbose old API doc can be found in the [old API.md](https://github.com/freifunk/openwifimap-api/blob/f9001452f4f4a72c4dbd59dd736436b6c5733775/API.md).

# License
openwifimap is licensed under the [MIT license](http://opensource.org/licenses/MIT).

# Operations

## Requirements

- PostgreSQL 11
- Python >= 3.6

## Install

* database
    * create a database user `owmuser`
    * create a database `owmdb`
    * connect to your postgres as superuser, e.g. by `sudo su - postgres` and execute `psql`
        * connect with your db: `\c owmdb`
        * create cube extension: `create extension cube;`
        * create earthdistance extension: `create extension earthdistance`
* service
    * change to the backend directory and install dependencies: `pip3 install -r requirements.txt`
    * create the directory `/var/opt/ffmapdata`
    * run the service: `python3 -m backend.main`

## Running with systemd

* Download [archive](https://github.com/freifunk/openwifimap-api/archive/refs/heads/master.zip), store and extract it (e.g. to `/opt/openwifimap-api`)
* Create a python virtual environment by running `python3 -m venv /path/to/openwifimap-venv`. Now you have the python binaries in `/path/to/openwifimap-venv/bin`
* Go to the directory with the extracted archive, change to the backend folder and install requirements by running `/path/to/openwifimap-venv/bin/pip3 install -r requirements.txt`
* Copy the included systemd file to `/etc/systemd/system/` and set the path to your venv binaries in `/path/to/openwifimap-venv/bin`
* Copy the systemd config file to `/etc/default/openwifimap-api` and configure the password for your database user

# Development info
The backend is basically keeping a list of JSON documents on disk which can get queried and updated via a web API.
The database is used as search index only.
PostgreSQL is total overkill for this but ¯\_(ツ)_/¯

The interesting part of the code is in [restapi.py](/backend/backend/restapi.py).

In case you wonder, endpoint definitions are a bit complicated (BaseModel, response_model, Field, Query, ...) since FastAPI can generate nice Swagger API docs from this.

## Dev notes
* sudo docker run --name owm_psql -p 127.0.0.1:5432:5432 -e POSTGRES_PASSWORD=<pwd> -e POSTGRES_USER=owmuser -e POSTGRES_DB=owmdb -d postgres:latest
* PostgreSQL earthdistance extension: https://postindustria.com/postgresql-geo-queries-made-easy/ (not used yet)

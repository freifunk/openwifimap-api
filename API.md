# The API

The openwifimap design document exposes an HTTP API for manipulating and querying the stored data. First you need to know the ```APIURL```. For the main openwifimap installation the ```APIURL``` is ```http://api.openwifimap.net/```. If you have your own installation and pushed the design document to ```http://myhost/mydb``` then the ```APIURL``` is ```http://myhost/mydb/_design/owm-api/_rewrite/``` (you can use a [CouchDB vhost](https://wiki.apache.org/couchdb/Virtual_Hosts) to obtain a nicer URL).

## Pushing data into the database
### node documents
Each node's data **must be updated at least once a day**. If a node is not updated for several days it is considered to be offline and may be removed from the database.

New nodes and node updates have to be pushed via a HTTP POST or PUT request to ```APIURL/update_node/ID``` where ```ID``` has to be replaced with the document's unique id. A node document has a few required fields (see above): ```type```, ```hostname```, ```latitude```, ```longitude``` and ```updateInterval```. The ```ctime``` and ```mtime``` are set automatically by the update handler.

The following example shows how to push a node with the id ```myid``` with curl:
```
curl -X POST http://myhost/mydb/_design/owm-api/_update/node/myid -d '{ 
  "type": "node",
  "hostname": "myhostname",
  "latitude": 52.520791,
  "longitude": 13.40951,
  "updateInterval": 6000
}'

```

<!--
### node_stats documents
A ```node_stats``` document only has two required fields: ```type``` and ```node_id```.

```node_stats``` docs have to be pushed via a HTTP POST or PUT request to ```_update/node_stats/```. The ```time``` field is set automatically.
-->

## Querying the database
### 

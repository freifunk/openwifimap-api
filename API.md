# The openwifimap API

The openwifimap design document exposes an HTTP API for manipulating and querying the stored data. First you need to know the ```APIURL```. For the main openwifimap installation the ```APIURL``` is ```http://api.openwifimap.net/```. If you have your own installation and pushed the design document to ```http://myhost/mydb``` then the ```APIURL``` is ```http://myhost/mydb/_design/owm-api/_rewrite/``` (you can use a [CouchDB vhost](https://wiki.apache.org/couchdb/Virtual_Hosts) to obtain a nicer URL).

## Pushing nodes into the database

Each node's data **must be updated at least once a day**. If a node is not updated for several days it is considered to be offline and may be removed from the database.

New nodes and node updates have to be pushed via a HTTP PUT request to ```APIURL/update_node/ID``` where ```ID``` has to be replaced with the document's unique id. A node document has a few required fields (see above): ```type```, ```hostname```, ```latitude```, ```longitude``` and ```updateInterval```. The ```ctime``` and ```mtime``` are set automatically by the update handler.

The following example shows how to push a node with the id ```myid``` with curl:
```
curl -X PUT APIURL/update_node/myid -d '{ 
  "type": "node",
  "hostname": "myhostname",
  "latitude": 52.520791,
  "longitude": 13.40951,
  "updateInterval": 6000
}'

```

<!--
### Pushing node_stats into the database
A ```node_stats``` document only has two required fields: ```type``` and ```node_id```.

```node_stats``` docs have to be pushed via a HTTP POST or PUT request to ```_update/node_stats/```. The ```time``` field is set automatically.
-->

## Querying the database
### By spatial bounding box

Let's get all nodes in a specific part of the earth that is defined by a bounding box. For example, all nodes in Berlin can be fetched with
```
curl "http://api.openwifimap.net/view_nodes_spatial?bbox=13.08,52.45,13.71,52.57"
```
which results in something like this:
```
{
  "update_seq": 21,
  "rows": [
    {
      "id": "derrida.olsr",
      ...
    },
    ...
  ]
}
```

However, sometimes there may be a lot of nodes in an area (imagine you zoomed out such that the full globe is visible). Then you first want to know how many nodes reside in a specific bounding box. Just add ```count=true```:
```
curl "http://api.openwifimap.net/view_nodes_spatial?bbox=13.08,52.45,13.71,52.57&count=true"
```
and you will see something like this:
```
{"count":2}
```

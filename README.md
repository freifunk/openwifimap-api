# openwifimap-api

OpenWiFiMap is a database and map for free network WiFi routers (freifunk and others, too!). 

This is the database part of the openwifimap. Make sure to also take a look at the [openwifimap HTML5 app](https://github.com/freifunk/openwifimap-html5) running at [openwifimap.net](http://openwifimap.net).

# API installations
This is a (possibly incomplete) list of API installations:
* [api.openwifimap.net](http://api.openwifimap.net)
* [couch.pberg.freifunk.net/test/_design/owm-api/_rewrite](http://couch.pberg.freifunk.net/test/_design/owm-api/_rewrite/)

# License
openwifimap is licensed under the [MIT license](http://opensource.org/licenses/MIT).

# API
See [openwifimap API](API.md).

## Document types
### node documents
#### Standard fields
The following fields are always present in a ```node``` document:
```javascript
{
  "_id": "a4d15a897f851938a799e548cc000eb0",      // required by CouchDB: document id
  "type": "node",                       // tells couchDB that this is a node
  "hostname": "myhostname",             // hostname == display name
  "latitude": 52.520791,                // latitude in degrees, range [-180,180], EPSG:3857
  "longitude": 13.40951,                // longitude in degrees, range [-90,90], EPSG:3857
  "updateInterval": 6000,               // time between consecutive updates in seconds
  "ctime": "2013-05-09T17:49:21.821Z",  // create time (automatically inserted by update handler, see below)
  "mtime": "2013-05-10T17:50:22.123Z"   // modify time (automatically inserted by update handler, see below)
}
```
#### Optional fields
While nothing is wrong with only pushing the required fields, you probably want to provide further information about the node. There are several fields that are recognized by the openwifimap couchapp, while you can add *any* other information about your node. Just make sure that you provide valid JSON and use the recognized fields correctly.

##### Links
The `links` field's value should be a list of links to neighbor nodes. Links between neighbors will be shown as lines in the map. The quality field is required for each field.
```javascript
  "links": [
    {
      "id": "a4d15a897f851938a799e548cc0017e7",  // document id of the neighbor node
      "quality": 1                               // quality of the link, range [0,1], 0==no link, 1==perfect link
    },
    {
      "id": "host2",
      "quality": 0.39016
    }
  ]
```
You can provide additional fields in link objects, for example the used routing protocol and its data in a mesh network (such as [OLSR](http://en.wikipedia.org/wiki/Optimized_Link_State_Routing_Protocol) or [B.A.T.M.A.N.](http://de.wikipedia.org/wiki/B.A.T.M.A.N.) in [freifunk](http://en.wikipedia.org/wiki/Freifunk) networks):
```javascript
  "links": [
    {
      "id": "host2",
      "quality": 0.39016,                 // for olsr, 1/etx can be used (be aware of dividing by zero)
      "olsr_ipv4": {                      // additional data
        "local_ip": "104.201.1.1",
        "neighbor_ip": "104.201.1.18",
        "lq": 0.533,
        "nlq": 0.732,
        "etx": 2.5631
      },
      "olsr_ipv6": {                      // additional data
        "local_ip": "2002:4e35:28e7:bd9d::1",
        "neighbor_ip": "2002:4e35:28e7:be2c::1",
        "lq": 0.533,
        "nlq": 0.732,
        "etx": 2.5631
      },
    }
  ]
```

##### Network interfaces and antennas
Each node can have several network interfaces. Provide as many details as possible to improve the presentation of the node in the map and on the detail page of OpenWiFiMap.
```javascript
  "interfaces": [
    // wire interface eth0
    {
      "name": "eth0",                    // required: name of the network interface
      "physicalType": "ethernet",        // required: either 'ethernet' or 'wifi'
      "macAddress": "00:66:77:88:99:AA", // the MAC address
      "maxBitrateRX": 100,               // max receive bitrate in Mbit/s
      "maxBitrateTX": 100,               // max transmit bitrate in Mbit/s
      "ipv4Addresses": [                 // list of ipv4 addresses+subnets in CIDR notation
        "104.201.0.29/28"
      ],
      "ipv6Addresses": [                 // list of ipv6 addresses+subnets in CIDR notation
        "dead:beef::2/56",
        "0455:dead::1235/64"
      ]
    },
    // wifi interface wlan0
    {
      "name": "wlan0",
      "physicalType": "wifi",
      "macAddress": "00:11:22:33:44:55",
      "maxBitrateRX": 300,
      "maxBitrateTX": 300,
      "ipv4Addresses": ["104.201.111.1/28"],
      "ipv6Addresses": ["1234:5678::1/64"],
      // wifi fields:
      "mode": "master",                     // 802.11 operation mode: 'master' (access point), 'client' or 'adhoc'
      "encryption": "none",                 // used encryption: 'none', 'wep', 'wpa', 'wpa2', ...
      "access": "free",                     // access policy:
                                            //   * 'free' as in freedom: use if everyone can use this network
                                            //     without password, prior registration and restrictions.
                                            //     This means no time limit or port restrictions!
                                            //     However, a splash screen with information fits into
                                            //     this definition.
                                            //   * 'password': use if everyone can obtain the password for free,
                                            //     and without registration, for example at the bar in your pub.
                                            //   * 'registration': use if everyone can use this network
                                            //     after registration but without any further restrictions.
                                            //   * 'restricted': use if time limits or port blocks are enforced
                                            //     in this network. Shame on you!
                                            //   * 'pay': use if users have to pay in order to use this network.
                                            //     Shame on you capitalist b4st4rd!
      "accessNote": "everyone is welcome!"  // a message explaining your access policy.
      "channel": 10,                        // channel number, see http://en.wikipedia.org/wiki/List_of_WLAN_channels
      "txpower": 15,                        // transmit power in dBm
      "bssid": "00:11:22:33:44:55",         // BSSID
      "essid": "liebknecht.freifunk.net",   // ESSID
      "dhcpSubnet": "104.201.111.1/28",     // offered ipv4 DCHP address subnet in CIDR notation
      "radvdPrefixes": [                    // list of advertised ipv6 prefixes in CIDR notation
        "1234:5678::/64"
      ],
      "antenna": {                          // description of the antenna that is attached to this interface
        "builtin": false,                   // is this antenna built into the device?
        "manufacturer": "IT ELITE",         // if isbuiltin==false: antenna manufacturer
        "model": "PAT24014",                // if isbuiltin==false: antenna model
        "type": "directed",                 // type of antenna: 'omni' or 'directed'
        "gain": 5,                          // antenna gain in dBi
        "horizontalDirection": 310,         // if type=='directed': horizontal direction of antenna in degrees, 
                                            //   range [0,360], 0 is north, 90 is east,... you got it!
        "horizontalBeamwidth": 120,         // horizontal beamwidth of antenna in degrees, range [0,360],
                                            //   value of 60 means that the antennas main beam is between
                                            //   horizontalDirection-30 and horizontalDirection+30 degrees
        "verticalDirection": -12.3,         // tilt of the antenna in degrees, range [-90,90],
                                            //   -90 means oriented towards ground, 0 parallel to ground,
                                            //   90 means oriented towards sky
        "verticalBeamwidth": 17,            // vertical beamwidth of antenna in degrees, range [-90,90],
                                            //   see horizontalBeamwidth
        "polarization": "vertical"          // polarization of antenna
      },
      "wireless": [
           {
               "ifname": "wlan0-1",
               "encryption": {
                   "enabled": false,
                   "auth_algs": [
                   ],
                   "description": "None",
                   "wep": false,
                   "auth_suites": [
                       "PSK"
                   ],
                   "wpa": 0,
                   "pair_ciphers": [
                   ],
                   "group_ciphers": [
                   ]
               },
               "bssid": "82:CA:FF:EE:BA:BE",
               "probereq": "1",
               "mode": "Ad-Hoc",
               "quality": 64,
               "noise": -95,
               "ssid": "ch8.freifunk.net",
               "up": "1",
               "device": "radio0",
               "bgscan": "0",
               "bitrate": 79000,
               "txpower": 19,
               "wirelessdevice": {
                   "type": "mac80211",
                   "disabled": "0",
                   "country": "DE",
                   "txpower": "19",
                   "ht_capab": [
                       "SHORT-GI-40",
                       "DSSS_CCK-40"
                   ],
                   "hwmode": "11ng",
                   "name": "radio0",
                   "channel": "8",
                   "macaddr": "d8:5d:XX:XX:19:b2",
                   "htmode": "HT20"
               },
               "channel": 8,
               "assoclist": [
                   {
                       "rx_short_gi": false,
                       "noise": -95,
                       "rx_mcs": 0,
                       "tx_40mhz": false,
                       "rx_40mhz": false,
                       "mac": "00:1E:XX:XX:6C:79",
                       "tx_rate": 54000,
                       "tx_packets": 265,
                       "tx_short_gi": false,
                       "rx_packets": 41061,
                       "tx_mcs": 0,
                       "inactive": 70,
                       "rx_rate": 5500,
                       "signal": -51
                   },
                   {
                       "rx_short_gi": false,
                       "noise": -95,
                       "rx_mcs": 0,
                       "tx_40mhz": false,
                       "rx_40mhz": false,
                       "mac": "54:E6:XX:XX:32:1E",
                       "tx_rate": 104000,
                       "tx_packets": 1192505,
                       "tx_short_gi": false,
                       "rx_packets": 11742264,
                       "tx_mcs": 13,
                       "inactive": 70,
                       "rx_rate": 5500,
                       "signal": -41
                   }
               ],
               "quality_max": 70,
               "network": "wireless0",
               "signal": -46
           }
       ],
    }
  ]
```

##### Community
```javascript
  "community": {
    "name": "Freifunk Berlin",
    "url": "http://berlin.freifunk.net/"
  }
```

##### Postal address
```javascript
  "postalAddress": {
    "name": "Café Kotti",
    "street": "  Adalbertstraße 96",
    "zip": "10999",
    "city": "Berlin",
    "country": "Germany"
  }
```

##### Firmware
```javascript
  "firmware": {
    "name": "openwrt",
    "revision": "r1234",
    "url": "http://firmware.pberg.freifunk.net/attitude_adjustment/12.09/ar71xx/openwrt-ar71xx-generic-ubnt-bullet-m-squashfs-factory.bin",
    "installed_packages": [ "olsrd", "dnsmasq", "kmod-ath9k" ]
  }
```

##### Hardware
```javascript
  "hardware": {
    "manufacturer": "Ubiquiti",
    "model": "Bullet M2"
    "revision": "3.5",
    "powersupply": "Ubiquiti PoE 24V"
  }
```

##### Other fields
```javascript
  "height": 15.5,                       // height in meters above ground level
  "indoor": true,                       // is this node placed indoors?
  "ipv4defaultGateway": "104.201.0.33",
  "ipv6defaultGateway": "dead:1337::1",
  "tags": [
    "Berlin",
    "freifunk",
    "Kreuzberg"
  ],
  "_attachments": {
    "avatar.jpg": {
      "content_type": "image/jpeg",
      "revpos": 9,
      "digest": "md5-s3yeZmYBgM4+UxbaNvQlsw==",
      "length": 84923,
      "stub": true
    }
  }
```


### node_stats documents
Dynamic data (such as statistics) can be stored in ```node_stats``` documents.  There are only these standard fields:
```javascript
{
  "_id": "e201d78aed2deee6982b4c07d6232abf",     // required by CouchDB: document id
  "type": "node_stats",                          // tells couchDB that this is a node_stats doc
  "node_id": "a4d15a897f851938a799e548cc000eb0", // id of the node this node_stats doc belongs to
  "time": "2013-05-10T17:58:34.829Z"             // time (automatically inserted by update handler, see below)
}
```


## Useful links
* Openwrt Packages: https://github.com/freifunk/packages-pberg/tree/master/utils/luci-app-owm
* Linux shell script: https://github.com/freifunk/ff-control/blob/master/scripts/dns-bonjour-geo-map.sh

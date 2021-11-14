## OpenWifiMap client for RouterOS

### Install

#### WebFig

* create a new script with name "owm-update"
* remove all permissioins beside "read"
* paste the script into the source textbox
* create a new scheduler with name "owm-update"
* change interval to "01:00:00"
* remove all permissioins beside "read"
* set script "owm-update" as the "on Event" action


### Configuration

Configuration can be done with the 3 variables in the topmost lines

* `owmapi`: Is the base-url of the OWM-Server (e.g. http://api.openwifimap.net).
* `location`: Is the JSON-encoded latitide and longitude that will be added to the JSON-dataset.
* `owmid`: Is optional and allows to define an ID for the dataset, which does not match the hostname. This is usually not needed and will default to the hostname.

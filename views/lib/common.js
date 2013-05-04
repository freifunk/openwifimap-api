exports.isnode = function(doc) {
  return (doc.type=='node' && doc.longitude && doc.latitude);
}

exports.spatial_nodes = function (doc, customdata) {
  var common = require('views/lib/common');
  if (common.isnode(doc)) {
    var data = customdata(doc);
    if (data) {
      data.id = doc._id;
      data.latlng = [doc.latitude, doc.longitude];
      data.links = doc.links;
      emit(
        { type: "Point", coordinates: [doc.longitude, doc.latitude] },
        data
      );
    }
  }
}

exports.view_nodes = function (doc, customdata) {
  var common = require('views/lib/common');
  if (common.isnode(doc)) {
    var data = customdata(doc);
    if (data) {
      data.id = doc._id;
      data.latlng = [doc.latitude, doc.longitude];
      emit(doc._id, data);
    }
  }
}

exports.view_nodes_coarse = function (doc, customdata) {
  var common = require('views/lib/common');
  var long2tile = function (lon,zoom) { 
    return (Math.floor((lon+180)/360*Math.pow(2,zoom))); 
  }
  var lat2tile = function (lat,zoom) { 
    return (Math.floor((1-Math.log(Math.tan(lat*Math.PI/180) + 1/Math.cos(lat*Math.PI/180))/Math.PI)/2 *Math.pow(2,zoom))); 
  }
  if (common.isnode(doc) && doc.latitude<85.0511 && doc.latitude>-85.0511) {
    var data = customdata(doc);
    if (data) {
      for (var zoom=0; zoom<=18; zoom++) {
        var x = long2tile(doc.longitude, zoom),
          y = lat2tile(doc.latitude, zoom);
        emit([zoom,x,y], 1);
      }
    }
  }
}

function (doc) {
  var common = require('views/lib/common');
  var custom = require('views/lib/custom');
  common.spatial_nodes(doc, custom.customdata);
}

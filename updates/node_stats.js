function (doc, req) {
  var newdoc = JSON.parse(req.body);
  if (newdoc.type != 'node_stats') {
    return [null, 'Error: type != node_stats']
  }
  if (doc) {
    return [null, 'Error: node stats should not be updated but newly created'];
  }

  newdoc._id = req.uuid;

  var date = (new Date()).toISOString();
  newdoc.time = date;

  return [newdoc, 'doc created with id ' + newdoc._id]
}

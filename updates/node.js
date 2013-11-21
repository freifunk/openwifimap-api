function (doc, req) {
  var newdoc = JSON.parse(req.body);
  if (newdoc.type != 'node') {
    return [null, 'Error: type != node'];
  }

  if (doc) {
    newdoc._id = doc._id;
    newdoc._rev = doc._rev;
  }

  // couchdb does not allow the prefix '_' as id for nodes
  if (!newdoc._id && req.id) {
    newdoc._id = req.id.replace(/^_+/, '');
  }

  if ('links' in newdoc) {
    for (var i = 0; i < newdoc.links.length; ++i) {
        link = newdoc.links[i];
        link.id = link.id.replace(/^_+/, '');
    }
  }

  var date = (new Date()).toISOString();
  newdoc.ctime = doc ? doc.ctime : date;
  newdoc.mtime = date;

  return [newdoc, 'doc updated'];
}

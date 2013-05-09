function (doc, req) {
  var newdoc = JSON.parse(req.body);
  if (newdoc.type != 'node') {
    return [null, 'Error: type != node'];
  }
  if (doc) {
    newdoc._id = doc._id;
    newdoc._rev = doc._rev;
  }

  var date = (new Date()).toISOString();
  newdoc.ctime = doc ? doc.ctime : date;
  newdoc.mtime = date;

  return [newdoc, 'doc updated'];
}

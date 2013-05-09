function (doc, req) {
  var newdoc = JSON.parse(req.body);
  if (doc) {
    newdoc._id = doc._id;
    newdoc._rev = doc._rev;
  }

  var date = (new Date()).toISOString();
  newdoc.ctime = doc ? doc.ctime : date;
  newdoc.mtime = date;

  return [newdoc, 'doc updated'];
}

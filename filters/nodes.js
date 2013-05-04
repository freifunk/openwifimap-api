function (doc, req) {
  if (doc._deleted) {
    return true;
  }
  if (doc.type && doc.type == 'node') {
    return true;
  } else {
    return false;
  }
}

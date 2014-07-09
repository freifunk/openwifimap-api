function(doc) {
  if (doc.type=='node') {
    emit(doc.mtime, {
      _rev: doc._rev
    });
  }
}

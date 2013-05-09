function (doc) {
  if (doc.type == 'node_stats') {
    emit([doc.node_id, doc.time], doc);
  }
}

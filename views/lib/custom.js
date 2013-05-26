exports.customdata = function (doc) {
  return {
    hostname: doc.hostname,
    antennas: doc.antennas,
    ctime: doc.ctime,
    mtime: doc.mtime
    // add any data you like here!
  }
}

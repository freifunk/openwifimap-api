function (newDoc, oldDoc, userCtx, secObj) {
  function required(field, message /* optional */) {
    if (!newDoc[field]) {
      throw({forbidden: message || "Document must have a " + field});
    }
  }

  function unchanged(field) {
    if (oldDoc && toJSON(oldDoc[field]) != toJSON(newDoc[field]))
      throw({forbidden: "Field can't be changed: " + field});
  }

  function isNumber(field, message) {
    if (typeof(newDoc[field]) != "number") {
      throw({forbidden: "Field must be a number: " + field});
    }
  }

  // tests if the field is a valid date
  // by checking invariance under ( new Date(...) ).toISOString()
  function isDate(field, message) {
    var date = (new Date(newDoc[field])).toISOString();
    if (newDoc[field] != date) {
      throw({forbidden: (message 
        || "Field "+field+" has to be invariant under (new Date(...)).toISOString() (evaluates to "+date+")") });
    }
    return date;
  }

  required('type');

  if (newDoc.type == 'node') {
    // cf. https://github.com/andrenarchy/openwifimap
    required('hostname');

    required('longitude');
    isNumber('longitude');
    if (newDoc['longitude'] < -90 || newDoc['longitude'] > 90) {
      throw({forbidden: 'invalid range: longitude should be between -90 and 90'});
    }

    required('latitude');
    isNumber('latitude');
    if (newDoc['latitude'] < -180 || newDoc['latitude'] > 180) {
      throw({forbidden: 'invalid range: latitude should be between -180 and 180'});
    }

    required('updateInterval');
    isNumber('updateInterval');

    required('ctime');
    unchanged('ctime');
    // check ctime and mtime (we allow the date to be 5 minutes in the future).
    var compare_time = (new Date( (new Date()).getTime() + 5*60*1000 )).toISOString();
    var ctime = isDate('ctime');
    if (ctime > compare_time) {
      throw({forbidden: 'future dates not allowed in field ctime: ' + newDoc['ctime']})
    }
    
    required('mtime');
    var mtime = isDate('mtime');
    if (mtime > compare_time) {
      throw({forbidden: 'future dates not allowed in field mtime: ' + newDoc['mtime']})
    }
    if (mtime < ctime) {
      throw({forbidden: 'mtime < ctime not allowed'});
    }
  } else {
    throw({forbidden: 'unrecognized type: ' + newDoc.type});
  }
}

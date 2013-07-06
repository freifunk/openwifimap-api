function (newDoc, oldDoc, userCtx, secObj) {
  //converts ISO datestamps to unix time stamps
  function timestamp(datestamp)
  {
    var pattern = new RegExp(/^([\d]{4})\-([\d]{2})\-([\d]{2})T([\d]{2}):([\d]{2}):([\d]{2})\.([\d]{3})(Z|(?:[+\-][\d]{2}[:]?[\d]{2}))$/);
    if(!pattern.test(datestamp))
    {
      return null;
    }
    var components = [], zoneoffset = 0;
    datestamp.replace(pattern, function(a,y,m,d,h,i,s,ms,z)
    {
      for(var bits = [y,m,d,h,i,s,ms], i = 0; i < 7; i ++)
      {
        components[i] = parseInt(bits[i], 10);
      }
      components[1]--;
      if(z !== 'Z')
      {
        zoneoffset =
        (
          (
            (parseInt((z = z.replace(':', '')).substr(1,2), 10) * 3600)
            +
            (parseInt(z.substr(3,4), 10) * 60)
          )
          *
          (z.charAt(0) == '-' ? 1000 : -1000)
        );
      }
  });
  return Date.UTC.apply(Date, components) + zoneoffset;
  }

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
  // we need a fallback for older javascript engines. They know .toISOString, but they're Date constructor can't create new Date objects with a given ISO formatted date stamp. so we convert the date ISO string to unix time and the use the toISOString function to evaluate the date
  function isDate(field, message) {
    var date = (new Date(newDoc[field])).toISOString();
    if ( date == "Invalid Date" ) {
      var newDate = (new Date(timestamp(newDoc[field]))).toISOString();
      date = newDate;
    }
    if (newDoc[field] != date) {
      throw({forbidden: (message
        || "Field "+field+" has to be invariant under (new Date(...)).toISOString() (evaluates to newDate: "+newDate+", date: "+date+", newDoc[field]: "+newDoc[field]+")  ") });
    }
    return date;
  }

  function user_is(role) {
    return userCtx.roles.indexOf(role) >= 0;
  }

  if (newDoc._deleted) {
    if (user_is('_admin')) {
      return;
    } else {
      throw({forbidden: 'Only admins are allowed to delete docs.'});
    }
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
      throw({forbidden: 'future dates not allowed in field ctime: ' + newDoc['ctime'] + ' cpt: ' + compare_time})
    }

    required('mtime');
    var mtime = isDate('mtime');
    if (mtime > compare_time) {
      throw({forbidden: 'future dates not allowed in field mtime: ' + newDoc['mtime']})
    }
    if (mtime < ctime) {
      throw({forbidden: 'mtime < ctime not allowed'});
    }
  } else if (newDoc.type == 'node_stats') {
    required('time');
    isDate('time');
    required('node_id');
  } else {
    throw({forbidden: 'unrecognized type: ' + newDoc.type});
  }
}

'''Run maintenance jobs for LibreMap.

This script runs the following maintenance jobs:

    * remove documents whose `mtime` is older than `days`.
'''
import argparse
import json
import couchdb
import datetime


def main():
    parser = argparse.ArgumentParser(
        description='Run maintenance jobs for LibreMap'
        )
    parser.add_argument(
        '--db',
        metavar='URL',
        help='couchDB URL'
        )
    parser.add_argument(
        '--days',
        metavar='DAYS',
        default=7,
        type=int,
        help='maximum age of a router document\'s mtime in days (default: 7)'
        )
    args = parser.parse_args()

    # create db object
    db = couchdb.client.Database(args.db)

    # get date for querying outdated routers
    date_diff = datetime.timedelta(days=args.days)
    date_now = datetime.datetime.utcnow()
    date_endkey = (date_now - date_diff).isoformat()

    # query and construct list of documents that are about to be deleted
    delete_docs = [
        {
            '_id': row.id,
            '_rev': row.value['_rev'],
            '_deleted': True
        }
        for row in db.view('owm-api/nodes_by_mtime',
                           endkey=date_endkey).rows
    ]

    # delete docs
    delete_res = db.update(delete_docs)

    nfail = 0
    for res in delete_res:
        if not res[0]:
            nfail += 1

    print('{0} documents have been deleted ({1} failed).'.format(
        len(delete_docs) - nfail,
        nfail))


if __name__ == '__main__':
    main()

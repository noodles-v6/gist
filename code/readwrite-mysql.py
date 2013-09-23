#!/usr/bin/env python
# -*- coding: utf8 -*-
import sys
import re
import time
import logging
import MySQLdb

from optparse import OptionParser
from datetime import datetime, timedelta

logger = logging.getLogger('conversion_tool')
logger.setLevel(logging.DEBUG)
#fh = logging.FileHandler('spam.log')
#fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG) # TODO
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#fh.setFormatter(formatter)
#ch.setFormatter(formatter)
#logger.addHandler(fh)
logger.addHandler(ch)

def convert_by_vddb(b):
    print "TODO: call vddb interface to convert live to nonlive"
    return [ b, 'a_meta_uuid_example_from_vddb' ]

def usage():
    print "[usage]: %s --host <host> --username"
    pass

if __name__ == "__main__":

    optparser = OptionParser()
    optparser.add_option('-H', '--host',     dest='host',    help = 'the host of database',     type='str')
    optparser.add_option('-u', '--username', dest='user',    help = 'the username of database', type='str')
    optparser.add_option('-P', '--port',     dest='port',    help = 'the port of database',     type='int')
    optparser.add_option('-p', '--password', dest='passwd',  help = 'the password of database', type='str')
    optparser.add_option('-d', '--database', dest='database',help = 'database',                 type='str')
    optparser.add_option('-x', '--duringtime',dest='time',help = 'check out the programs before N in minutes', type='int')

    (options, args) = optparser.parse_args()

    host = options.host
    user = options.user
    port = options.port
    passwd = options.passwd
    database = options.database
    duringtime = options.time

    if host is None or user is None or port is None or \
           passwd is None or database is None or duringtime is None :
        print "Error! parameter settings are missing\nPleasee check out `%s --help`" % sys.argv[0]
        exit(1)

    logger.debug("parameters: host=%s, user=%s, passwd=%s, db=%s, port=%d, duringtime=%d" % (host, user, passwd, database, port, duringtime))

    conn = None
    try:
        conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=database, port=port)
        cur = conn.cursor()

        cmptime = (datetime.now() - timedelta(hours=duringtime)).strftime('%Y-%m-%d %H:%M:%S')

        ### 1
        sql = "select id from msync_meta_server.content where start_at >= %s and translate_status = %s"
        cur.execute(sql, (cmptime, 'processing'))

        rows = cur.fetchall()
        for row in rows:
            content_id = row[0]
            # TODO 这里到等VDDB接口
            success, meta_uuid = convert_by_vddb(content_id%2 == 0)

            if success:
                insert_sql = "insert into nonliveMeta (meta_uuid, company_id) values (%s, 1)"
                cur.execute(insert_sql, (meta_uuid))

                update_sql = "update content set uuid=%s, translate_status=%s where id=%s";
                cur.execute(update_sql, (meta_uuid, 'success', content_id))
            else:
                logger.error("convert live to nonlive by VDDB (meta_uuid=%s)", (meta_uuid))

        #### 2
        sql2 = "select id from msync_meta_server.content where start_at < %s"
        cur.execute(sql2, (cmptime))

        rows = cur.fetchall()
        for row in rows:
            content_id = row[0]
            update_sql = "update content set translate_status=%s where id=%s"
            cur.execute(update_sql, ('fail', content_id))

        conn.commit()
        cur.close()
        conn.close()

    except MySQLdb.Error, e:
        logger.exception(e)
        if conn:
            conn.rollback()
    except Exception, e:
        logger.exception(e)
        if conn:
            conn.rollback()


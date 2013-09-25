#!/usr/bin/env python
# -*- coding: utf8 -*-
import re
import sys
import os
import time
import json
import logging
import logging.config
import ConfigParser
import MySQLdb
from datetime import datetime, timedelta

# the major dirs
bin_dir = os.path.dirname(os.path.abspath(__file__))
if os.path.islink(os.getenv('PWD')):
    bin_dir = os.getenv('PWD')
run_dir = os.getenv('PWD')
os.chdir(bin_dir)

base_dir = os.path.dirname(bin_dir)
conf_dir = os.path.join(base_dir, 'conf')
log_dir  = os.path.join(base_dir, 'log')
lib_dir  = os.path.join(base_dir, 'lib')
receipt_dir = os.path.join(base_dir, 'receipt')


###########################

def convert_by_vddb( content_id, channel_uuid, start_at, end_at ):
    during = (end_at - start_at).seconds
    start_at = start_at.strftime('%Y-%m-%d %H:%M:%S').replace(' ', 'T').replace('-','')
    timestamp = time.time()
    receipt_file = os.path.join(receipt_dir, "receipt."+channel_uuid+".json."+str(timestamp))

    cmd = "python %s/live2nonlive/bin/live2nonlive.py -c %s -s %s -d %d --out_format=json --receipt %s" \
            % (lib_dir, channel_uuid, start_at, during, receipt_file)

    ret = os.system(cmd)
    if ret != 0:
        return [ ret, '']

    jresult = json.loads( open(receipt_file).read() )
    return [ int(jresult['receipt']['ErrorCode']), jresult['receipt']['ContentID'] ]

if __name__ == "__main__":

    # init logging
    logger = None
    try: 
        log_file = os.path.join(log_dir, datetime.now().strftime("%Y%m%d%H%M%S"))
        log_name = 'live2nonlive'
        logging.config.fileConfig(os.path.join(conf_dir, "logging.conf"))
        logger = logging.getLogger(log_name)
    except Exception, e:
        print >> sys.stderr, "logging initialization failed: %s" % str(e)
        sys.exit(-1)


    # init database
    conf = ConfigParser.ConfigParser()
    conf.read(os.path.join(conf_dir, "app.conf"))

    host = conf.get('database', 'host')
    user = conf.get('database', 'username')
    port = int(conf.get('database', 'port'))
    passwd     = conf.get('database', 'password')
    database   = conf.get('database', 'db')
    duringtime = int(conf.get('app', 'during'))

    if host is None or user is None or port is None or \
       passwd is None or database is None or duringtime is None :
        print "Error! parse db.conf exception"
        exit(-1)

    conn = None
    try:
        conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=database, port=port)
        cur = conn.cursor()

        cmptime = (datetime.now() - timedelta(hours=duringtime)).strftime('%Y-%m-%d %H:%M:%S')

        sql = "select id, uuid, start_at, end_at "\
              "from msync_meta_server.content "\
              "where ((start_at >= %s and translate_status='fail') or translate_status='processing') and is_deleted='false' "\
              "order by id asc"
        cur.execute( sql, (cmptime) )

        rows = cur.fetchall()
        for row in rows:
            logger.info(row)
            (content_id, channel_uuid, start_at, end_at) = row
            (success, meta_uuid) = convert_by_vddb( content_id, channel_uuid, start_at, end_at )

            try:
                if success == 0:
                    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    insert_sql = "insert into nonliveMeta (meta_uuid, company_id, created_at, updated_at) values (%s, 1, %s, %s)"
                    cur.execute( insert_sql, (meta_uuid, now, now ))

                    update_sql = "update content set uuid=%s, translate_status=%s where id=%s";
                    cur.execute( update_sql, (meta_uuid, 'success', content_id) )

                    logger.info('live2nonlive success')
                else:
                    update_sql = "update content set translate_status=%s where id=%s";
                    cur.execute( update_sql, ('fail', content_id) )
                    logger.error("live2nonlive failed")
            except Exception, e:
                 logger.exception(e)
                 conn.rollback()
            finally:
                 conn.commit()

        update_all_expired_fail= "update msync_meta_server.content "\
                                 "set translate_status='fail'"\
                                 "where start_at < %s and translate_status != 'fail'"
        cur.execute(update_all_expired_fail, (cmptime))
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


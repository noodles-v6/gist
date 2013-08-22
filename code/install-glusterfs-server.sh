#!/usr/bin/env bash

apt-get install glusterfs-server

glusterfsd –version

if [ ! -e /data ] ; then
    sudo mkdir /data 
fi

gluster volume create tvsr 192.168.10.62:/data

if [ $? == "0" ]; then
    gluster volume start tvsr 
else 
    echo "Fail:  gluster volume create tvsr 192.168.10.62:/data"
    exit 1
fi

gluster volume info 

gluster volume set tvsr auth.allow 192.168.10.44

if [ $? != "0" ]; then 
    echo "Fail:  gluster volume set tvsr auth.allow 192.168.10.44"
else
    echo "OK"
fi



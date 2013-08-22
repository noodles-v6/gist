#!/usr/bin/env bash

apt-get install glusterfs-client

if [ ! -e /mnt/glusterfs ]; then
    mkdir /mnt/glusterfs
fi

mount.glusterfs 192.168.10.62:/tvsr /mnt/glusterfs

mount

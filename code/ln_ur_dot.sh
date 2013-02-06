#!/bin/sh 

pwd=`pwd`
for i in dot.*
do 
    s=`echo $i | sed -e s/^dot//`
    if [ -e $HOME/$s/]
    then 
        mv $HOME/$s $HOME/$s.bak
    fi
    ln -s $pwd/$i $HOME/$s 
done

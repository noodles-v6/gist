#!/bin/bash

#http://stackoverflow.com/questions/592620/check-if-a-program-exists-from-a-bash-script
type wget >/dev/null 2>&1 || {

curl -o wget-1.14.tar.gz http://ftp.gnu.org/gnu/wget/wget-1.14.tar.gz

tar zxvf wget-1.14.tar.gz

cd wget-1.14

./configure  --with-ssl=openssl

make
sudo make install
make clean

cd ..

rm -rf wget*
}

if type wget >/dev/null 2>&1; then
  echo "install wget ok."
else
  echo "install wget error."
fi

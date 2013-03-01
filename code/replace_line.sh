
# 把/path/to目录下的文件中127.0.0.1地址改为192.168.1.1
find /path/to -type f | xargs -n 1 sed -i 's/127.0.0.1/192.168.1.1/g' 

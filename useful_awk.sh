# 来源于：http://mylinux.5d6d.com/thread-200-1-1.html
 
# passwd文件中把所有www替换为abc
awk 'gsub(/www/,"abc")' /etc/passwd
 
# 替换$1中的www为abc
awk -F ':' 'gsub(/www/,"abc",$1) {print $0}' /etc/passwd
 
# passwd文件中把第一次出现的www替换为abc
awk 'sub(/www/,"abc")' /etc/passwd

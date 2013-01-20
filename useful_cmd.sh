#
# strings命令可以查看非文本里文本内容，具体man strings
# 下面的语句可以打印出CREATE TABLE语句
#
strings expdp.dmp | grep "CREATE TABLE"| sed -e 's/,/,\n/g'

#
# 片段来源于：http://www.softpanorama.org/Scripting/Perlorama/perl_in_command_line.shtml
# 下面的代码做了简单的文本替换工作
#
 
find . -type f -exec perl -i -pe 's/something/another/g' {} \;

# 处理回车符
# TODO  看看结果怎样
IFS=$'\n'
(IFS=$'\n';for i in $(< a.txt);do echo $i;done)

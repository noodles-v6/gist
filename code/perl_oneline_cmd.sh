# 1. 打印文件的mode
# 来自于：http://www.commandlinefu.com/commands/view/10466/perl-oneliner-to-print-access-rights-in-octal-format?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+Command-line-fu+%28Command-Line-Fu%29
# 发现 http://perldoc.perl.org/functions/stat.html 有个基本一样的语句。
perl -e 'printf "%04o\n", (stat shift)[2] & 0777;' file
 
# 2. 文本替换备份
# http://www.softpanorama.org/Scripting/Perlorama/perl_one_liners.shtml
perl -i.bak -pe 's/pattern1/pattern2/g' inputFile
 
# 3. unix2dos的Perl实现
perl -i.bak -pe 's/\n/\r\n/' filename 
 
# 4. 选择两个匹配模式下的行
perl -i.old -ne 'print unless /pattern1/ .. /pattern2/' filename
# 比如
perl -i.old -ne 'print unless /^START$/ .. /^END$/' filename
 
# 5. 打印文本时带上行号
perl -ne '$i++;print"$i\t$_";' filename
 
# 6. Print balance of quotes in each line (useful for finding missing quotes in Perl and other scripts) 
perl -ne '@F=split;for $s (@F){ $j++ if $s eq q(")}; $i++;print"$i\t$j\t$_";' filename
 
# 7. Emulation of Unix cut utility in Perl. 
# Option -a ( autosplit mode) converts each line into array @F. 
# The pattern for splitting a whitespace (space or \t) and unlike cut it accommodates consecutive spaces of \t mixes with spaces.   
# Here's a simple one-line script that will print out the fourth word of every line, but also skip any line beginning with a # because it's a comment line.
perl -naF 'next if /^#/; print "$F[3]\n"'
perl -lane 'print "$F[0]:$F[-2]\n"'

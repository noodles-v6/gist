#!/usr/bin/perl

$n = <>;

$old = 0; # 成年兔子个数
$new = 1; # 幼年兔子个数
$sum = 1; # 所有兔子个数

while (1) {
  $sum = $old + $new;

	last if $sum > $n;
	
	print $sum, "\n";
	# 一个月后
	$new = $old; # 一个月前的成年兔子都产下一个幼兔
	$old = $sum; # 一个月前所有的兔子现在都可以繁重了,成为了成年兔子
}

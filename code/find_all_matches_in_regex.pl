# http://stackoverflow.com/questions/1723440/how-can-i-find-all-matches-to-a-regular-expression-in-perl
 
#!/usr/bin/perl
 
use strict; 
use warnings;
 
my $str = <<EO_STR;
Name=Value1
Name=Value2
Name=Value3
EO_STR
 
my @matches = $str =~ /=(\w+)/g;
# or my @matches = $str =~ /=([^\n]+)/g;
# or my @matches = $str =~ /=(.+)$/mg;
# depending on what you want to capture
 
print "@matches\n";

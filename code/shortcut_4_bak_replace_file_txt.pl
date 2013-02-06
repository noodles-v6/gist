#!/usr/bin/perl -w
 
use strict;
 
@ARGV = qw/ a.txt /;
 
$^I = ".bak";
 
while(<>)
{
    s/4/5/g;
    print ;
}

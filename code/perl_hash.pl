#!/usr/bin/perl -w
 
use strict;
use Data::Dumper;
 
my %hash;
 
# `push` is working on an array. @{...} is making each element of the hash reference an array
 
#push @{$hash{'1'}}, '1home';
push @{$hash{'1'}{'a'}}, '1a';
push @{$hash{'1'}{'b'}}, '1b';
 
#push @{$hash{'2'}}, '2home';
push @{$hash{'2'}{'a'}}, '2a';
 
print Dumper %hash;

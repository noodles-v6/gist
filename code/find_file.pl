#!/usr/bin/perl 

use v5.10;
use File::Find;

my @dirs = ( '.' );

find(\&print_name, @dirs);

sub print_name{
    my $path;
    if (/\.cpp/) {
        $path = $File::Find::name;
        say $path;
    }
}

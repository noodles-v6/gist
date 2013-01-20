#!/usr/bin/perl 

use v5.12;
use strict;
use warnings;

$_ = "foobar";

my $t = /foo/;

say $t;

my ($new, $old);
($new = $old) =~ s/foo/bar/g;

say $new;
say $old;

print <<"EOF";
:   hello perl;
:   hey world;
:
EOF


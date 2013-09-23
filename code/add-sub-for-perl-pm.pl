#!/usr/bin/env perl

package Foo::Bar;

use Moo;

sub vvv {
    my $self = shift;
}

1;

package main;

use Smart::Comments;

my $foo = Foo::Bar->new;

my $brain = sub {
    my $foo = shift;
    ### foo: $foo
    print "Foo::Bar hasn't the brain subroutine, but it's invoked by foo! yeah, I love Perl deeper!\n";
};

$foo->$brain;

1;

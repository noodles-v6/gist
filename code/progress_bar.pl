#!/usr/bin/env perl

do {
    progress_bar( $_, 100, 25, '=');
    sleep 1
} for 1 .. 100;

sub progress_bar {
    my ($got, $total, $width, $char) = @_;
    $width ||= 25;
    $char  ||= '=';
    my $num_width = length $total;
    local $| = 1;
    printf "|%-${width}s| Got %${num_width}s bytes of %s (%.f%%)\r",
        $char x (($width-1)*$got/$total). '>', 
        $got, 
        $total, 
        100*$got/$total;
}

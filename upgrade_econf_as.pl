#!/usr/bin/perl 

use strict;
use warnings;
use IO::Prompt;
use Data::Dumper;

print <<EOC;
The Tool will help you update a remote EConfAS service from 
local. Please do updation via the instructions.
EOC

while (1) {
    my $opt = prompt 'Select an item to update:',
            -menu => {
                'CMU' => 1,
                'Focus' => 2,
                'CRU' => 3,
                'Ptcpt' => 4,
                'Rollback' => 5,
                'Quit' => 6,
            };

    if    ($opt == 1) { &update_cmu }
    elsif ($opt == 2) { &update_focus }
    elsif ($opt == 3) { &update_cru }
    elsif ($opt == 4) { &update_ptcpt }
    elsif ($opt == 5) { print "start rollback\n";  }
    elsif ($opt == 6) { exit 0 }
}

sub update_cmu {
    print "update CMU start..\n";
}

sub update_focus {

}

sub update_cru {

}

sub update_ptcpt {

}
        



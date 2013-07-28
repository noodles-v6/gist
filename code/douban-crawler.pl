#!/usr/bin/env perl
 
use 5.010;
use open qw(:locale);
use strict;
use utf8;
use warnings qw(all);

use Mojo::UserAgent;

my @urls = map { Mojo::URL->new(
    "http://www.douban.com/group/topic/38829294/?start=".100*$_) 
} (0..31);

my $ua = Mojo::UserAgent
    ->new(max_redirects => 5)
    ->detect_proxy;

my $max_conn = 4;
my $active   = 0;

Mojo::IOLoop->recurring(
    0 => sub {
        for ($active+1 .. $max_conn) {

            return ($active or Mojo::IOLoop->stop)
                unless my $url = shift @urls;

            ++$active;
            $ua->get($url => \&get_callback);
        }
    }
);

Mojo::IOLoop->start unless Mojo::IOLoop->is_running;

sub get_callback {
    my (undef, $tx) = @_;

    --$active;

    return
        if not $tx->res->is_status_class(200)
            or $tx->res->headers->content_type !~ m{^text/html\b}ix;

    my $url = $tx->req->url;
    
    parse_html($url, $tx);

    return;
}

sub parse_html {
    my ($url, $tx) = @_;

    for my $e ($tx->res->dom->find('div[class="reply-doc content"]')->each) {
        my $people = $e->at('h4')->at('a')->text;
        my $p_txt  = $e->at('p[class]')->text;
        if ($p_txt =~ /^.*[^\d]?0?2[^\d]?13/) {
            say "\@$people => $p_txt";
        }
    }
}

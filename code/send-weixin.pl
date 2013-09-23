#!/usr/bin/env perl

use 5.010;
use strict;
use utf8;
use warnings qw(all);
use Mojo::UserAgent;
use Smart::Comments;

my $url = 'https://mp.weixin.qq.com/cgi-bin/login?lang=zh_CN';

my $ua = Mojo::UserAgent->new( max_redirects => 5 )->detect_proxy;

my $header = {
    'Host'             => 'mp.weixin.qq.com',
    'Connection'       => 'keep-alive',
    'Accept'           => '*/*',
    'Origin'           => 'https://mp.weixin.qq.com',
    'X-Requested-With' => 'XMLHttpRequest',
    'Content-Type'    => 'application/x-www-form-urlencoded; charset=UTF-8',
    'Referer'         => 'https://mp.weixin.qq.com/',
    'Accept-Encoding' => 'gzip,deflate,sdch',
    'Accept-Language' => 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3'

    #'User-Agent' =>  'Mozilla/5.0',
};

my $tx = $ua->post(
    $url => $header => form => {
        username => 'shiwendunyin',
        pwd      => 'f74d39fa044aa309eaea14b9f57fe79c',
        f        => 'json'
    }
);

my $cookie = $tx->res->cookies;
### $cookie

if ( my $res = $tx->success ) {
    say $res->body;
}
else {
    my ( $err, $code ) = $tx->error;
    say $code ? "$code response: $err" : "Connection error: $err";
}

#### Send ####

my $send_url = 'https://mp.weixin.qq.com/cgi-bin/singlesend';

my $send_header = {
    Host               => 'mp.weixin.qq.com',
    Connection         => 'keep-alive',
    Accept             => 'text/html, */*; q=0.01',
    Origin             => 'https://mp.weixin.qq.com',
    'X-Requested-With' => 'XMLHttpRequest',
    'Content-Type'     => 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept-Encoding'  => 'gzip,deflate,sdch',
    'Accept-Language'  => 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
    Referer =>
'https://mp.weixin.qq.com/cgi-bin/message?t=message/list&count=20&day=7&token=1563563447&lang=zh_CN',
};

my $send_tx = $ua->build_tx(
    POST => $send_url => $send_header => form => {
        mask         => 'false',
        tofakeid     => 674816982,
        type         => 1,
        content      => 'rrrrww',
        quickreplyid => 30,
        token        => 1563563447,
        lang         => 'zh_CN',
        t            => 'ajax-response'
    }
);

$send_tx->req->cookies( $cookie );
$ua->start($send_tx);

#!/usr/bin/env perl

use strict;
use warnings;

my %values;

$values{1}{0} 	     =  -5;
$values{1}{9} 	     =   5;
$values{10000000}{0} = -10;
$values{10000000}{9} =  10;

for my $j (0..9) {
	for my $i (qw(1 10 100 1000 10000 100000 1000000 10000000)) {
		my $value = 0;
		$value = $values{$i}{$j} if exists $values{$i}{$j};
		print "$i, $j, $value\n";
	}
}


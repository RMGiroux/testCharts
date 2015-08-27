#!/usr/bin/env perl

use strict;
use warnings;

my $test_run=10;

my @powers = map {2**$_} 0..8;

my %datapoints;

$datapoints{1}  {0}         = -3;
$datapoints{1}  {$test_run} =  3;
$datapoints{256}{0}         =  5;
$datapoints{256}{$test_run} = -5;

foreach my $power(@powers) {
	for (my $i=$test_run; $i>=0; --$i) {
		my $value = 0;
		$value = $datapoints{$power}{$i} if exists $datapoints{$power}{$i};
		print "$test_run, $i, $power, $value\n";
	}
}

#!/usr/bin/env perl

use strict;
use warnings;

$|++;

my $debug = 1;

my %files = (
	WITH => 'processed_test_data-with-allocators.out'
      , WITHOUT => 'processed_test_data-without-allocators-without-0.out'
);

my %values;

foreach my $filetype(keys %files) {
	my $filename=$files{$filetype};
	open(IN, "<", $filename) or die "Can't open $filename, error $!";

	while(<IN>) {
		my ($key, $value) = m{(^.*,)(.*)};
		print STDERR "$filetype: $key $value\n";

		$values{$key}{$filetype} = $value;
	}
}

foreach my $key(sort keys %values) {
	next unless exists $values{$key}{WITHOUT}
		and exists $values{$key}{WITH};
	printf "$key %f\n", $values{$key}{WITHOUT}/$values{$key}{WITH};
}

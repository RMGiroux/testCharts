#!/usr/bin/env perl

use strict;
use warnings;

$|++;

sub average {
	my $list_r = shift;

	my $count = @$list_r;
	my $sum   = 0;

	$sum += $_ foreach @$list_r;

	$sum /= $count if $count;

	return $sum;
}

sub safeDiv {
	my ($num, $den) = @_;

	if(!$den) {
		return "NAN";
	}
	
	return $num/$den;
}

for my $infile(<oz*>) {
	# Everything below 15 is noise - JSL
	next unless $infile ge "oz15";

	print STDERR "Processing $infile\n";
	local $/;

	$/ = "\nsys\t";

	my %realTimes;  # Keys: {ns}{iL}{cc}{it}
	my @baseRealTimes;
	my $averageRealTime = -9999;

	my %seenKeys;
	my @keys;

	my $prevKey = "";

	open(my $in, "<", $infile) or die "Can't open $infile, error $!";
	RECORD: while(<$in>) {
		if (m{^nS = -(\d+)\s+iL = (\d+).*?cC = (-?\d+)\s+it = (\d+).*real\s+(\d+)m(\d+\.\d+)}ms) {
			my ($ns, $iL, $cc, $it, $minutes, $seconds) = ($1, $2, $3, $4, $5, $6);

			my $time = $minutes*60+$seconds;

			if ($it == 0) {
				push @baseRealTimes, $time;
				next RECORD;
			}
			elsif ($averageRealTime == -9999) {
				$averageRealTime = average(\@baseRealTimes);
				print "Average is $averageRealTime\n";
			}
			$time -= $averageRealTime;

			my $key = "$ns/$iL/$it";

			push @keys, [$ns, $iL, $it] if !$seenKeys{$key}++;

			die "Reused key!" if exists $realTimes{$ns}{$iL}{$cc}{$it};
			$realTimes{$ns}{$iL}{$cc}{$it} = $time;
			die "Missing key!" unless exists $realTimes{$ns}{$iL}{$cc}{$it};

			#printf "==== $ns, $iL, $it, $cc, %f\n", $time;
		}
	}

	foreach my $key(@keys) {
		my ($ns, $iL, $it) = @$key;

		if (exists($realTimes{$ns}{$iL}{-5}{$it})
				and exists($realTimes{$ns}{$iL}{5}{$it})) {
			printf "$ns, $iL, $it, %s\n", safeDiv($realTimes{$ns}{$iL}{5}{$it},
												  $realTimes{$ns}{$iL}{-5}{$it});
	    }
	}
}

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

for my $infile(<shuffleData/o*>) {
    next if $infile =~ /o9$|o10$/;

	print STDERR "Processing $infile\n";

	local $/;
	$/ = "\nsys\t";

	my %realTimes;  # Keys: {ns}{iL}{cc}{it}
	my @baseRealTimes;
	my $averageRealTime = -9999;

	my $timeDelta = 3.65;  # Cost of each level of shuffles
	my $costOf0Shuffles = 3.38;

	my %seenKeys;
	my @keys;

	my $prevKey = "";

	open(my $in, "<", $infile) or die "Can't open $infile, error $!";
	RECORD: while(<$in>) {
		if (m{^nS = (\d+)\s+iL = (\d+).*?cC = (-?\d+)\s+it = (\d+).*real\s+(\d+)m(\d+\.\d+)}ms) {
			my ($ns, $iL, $cc, $it, $minutes, $seconds) = ($1, $2, $3/10000000, $4, $5, $6);

			my $time = $minutes*60+$seconds;

			#$time -= $timeDelta * abs($cc);

			my $key = "$ns/$iL/$it/$cc";
            #print STDERR "===  $key, $time\n";

			push @keys, [$ns, $iL, $it, $cc] if !$seenKeys{$key}++;

			die "Reused key!" if exists $realTimes{$ns}{$iL}{$cc}{$it};
			$realTimes{$ns}{$iL}{$cc}{$it} = $time;
			die "Missing key!" unless exists $realTimes{$ns}{$iL}{$cc}{$it};

			#printf "==== $ns, $iL, $it, $cc, %f\n", $time;
		}
	}

	foreach my $key(@keys) {
		my ($ns, $iL, $it, $cc) = @$key;

        next if $cc < 0;

		my $ratio = ($realTimes{$ns}{$iL}{$cc}{$it} - $realTimes{$ns}{$iL}{-$cc}{$it})/$costOf0Shuffles;

        printf STDERR "$ns, $cc, %s, %s, %s\n",$realTimes{$ns}{$iL}{$cc}{$it},$realTimes{$ns}{$iL}{-$cc}{$it}, $ratio;

        printf "$ns, $cc, %s\n", $ratio;

        if ($ratio<-1 || $ratio>25) {
            print STDERR "Ratio $ratio for $ns, $iL, $it is strange!\n"
	    }
	}
}

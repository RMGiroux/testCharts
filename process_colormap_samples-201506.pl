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

if (@ARGV) {
	chdir $ARGV[0] or die "Unable to cd to $ARGV[0], error $!";
}

for my $infile(<oz*>) {
	# Everything below 15 is noise - JSL
	next unless $infile ge "oz15";

	print STDERR "Processing $infile\n";
	local $/;

	my %realTimes;  # Keys: {ns}{iL}{cc}{it}
	my @baseRealTimes;
	my $averageRealTime = -9999;

	my %seenKeys;
	my @keys;

	my $prevKey = "";

	open(my $in, "<", $infile) or die "Can't open $infile, error $!";
	local $/;
	local $_ = <$in>;
	while (m{^nS = -(\d+)\s+iL = (\d+)\s+aC = (\d+).*?cC = (-?\d+)\s+it = (\d+).*?(\d+):(\d+\.\d+)}msg) {
		my ($ns, $iL, $aC, $cc, $it, $minutes, $seconds) = ($1, $2, $3, $4, $5, $6, $7);

		my $time = $minutes*60+$seconds;

		my $key = "$ns/$iL/$it/$aC";

		push @keys, [$ns, $iL, $it, $aC] if !$seenKeys{$key}++;

		die "Reused key!" if exists $realTimes{$ns}{$iL}{$cc}{$it}{$aC};
		$realTimes{$ns}{$iL}{$cc}{$it}{$aC} = $time;
		die "Missing key!" unless exists $realTimes{$ns}{$iL}{$cc}{$it}{$aC};

		#printf "==== $ns, $iL, $aC, $it, $cc, %f\n", $time;
	}

	foreach my $key(@keys) {
		my ($ns, $iL, $it, $aC) = @$key;

		next unless $aC;

		if (exists($realTimes{$ns}{$iL}{-5}{$it}{$aC})
				and exists($realTimes{$ns}{$iL}{5}{$it}{$aC})
				and exists($realTimes{$ns}{$iL}{-5}{$it}{0})
				and exists($realTimes{$ns}{$iL}{5}{$it}{0})) {
			my $averageBaseTime = ($realTimes{$ns}{$iL}{-5}{$it}{0}
			                     + $realTimes{$ns}{$iL}{5}{$it}{0})
			                     / 2;
			my $baseTimeDelta = abs($realTimes{$ns}{$iL}{-5}{$it}{0}
			                     - $realTimes{$ns}{$iL}{5}{$it}{0})
			                     / $realTimes{$ns}{$iL}{-5}{$it}{0};
			printf STDERR "Base times for $ns/$iL/$it ($realTimes{$ns}{$iL}{-5}{$it}{0}, "
			           . "$realTimes{$ns}{$iL}{5}{$it}{0}) differ by more than 2%% (%f %%)\n",
			           $baseTimeDelta if $baseTimeDelta>2;

			my $ratio = safeDiv($realTimes{$ns}{$iL}{5}{$it}{$aC} - $averageBaseTime,
			                    $realTimes{$ns}{$iL}{-5}{$it}{$aC} - $averageBaseTime);

			printf "$ns, $iL, $it, %s\n", $ratio;

			if ($ratio<-1 || $ratio>15) {
			    print STDERR "Ratio $ratio for $ns, $iL, $it is strange!\n";
			    printf STDERR "\taverageBaseTime               = %f\n",
			    			  $averageBaseTime;
			    printf STDERR "\tnumerator (pre-subtraction)   = %f\n",
			     			  $realTimes{$ns}{$iL}{5}{$it}{$aC};
			    printf STDERR "\tdenominator (pre-subtraction) = %f\n",
			     			  $realTimes{$ns}{$iL}{-5}{$it}{$aC};
			}
	    }
	}
}

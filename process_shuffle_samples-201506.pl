#!/usr/bin/env perl

use strict;
use warnings;

$|++;

my $debug = 1;

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

my %realTimes;  # Keys: {ns}{iL}{cc}{it}

for my $infile(<o*>) {
    next if $infile =~ /o9$|o10$/;

	print STDERR "Processing $infile\n";

	local $/;
	$/ = "swaps\n";

	my @baseRealTimes;
	my $averageRealTime = -9999;

	my $timeDelta = 3.65;  # Cost of each level of shuffles
	my $costOf0Shuffles = 3.38;

	my %seenKeys;
	my @keys;

	my $prevKey = "";

	open(my $in, "<", $infile) or die "Can't open $infile, error $!";
	RECORD: while(<$in>) {
    	#while (m{^nS = -(\d+)\s+iL = (\d+)\s +aC = (\d+).*?aC = (\d+).*?cC = (-?\d+)\s+it = (\d+).*?(\d+):(\d+\.\d+).*?$}msg) {
		if (m{^nS = (\d+)\s+iL = (\d+).*?aC = (\d+)\s+cC = (-?\d+)\s+it = (\d+).*?(\d+):(\d+\.\d+)elapsed.*?$}ms) {
			my ($ns, $iL, $ac, $cc, $it, $minutes, $seconds) = ($1, $2, $3, $4/10000000, $5, $6, $7);

			next RECORD if $ac == 0;

			my $time = $minutes*60+$seconds;

			#$time -= $timeDelta * abs($cc);

			my $key = "$ns/$iL/$it/$cc";
            #print STDERR "===  $key, $time\n";

			push @keys, [$ns, $iL, $it, $cc] if !$seenKeys{$key}++;

			if (exists $realTimes{$ns}{$iL}{$cc}{$it}) {
				warn "Reused key ($ns/$iL/$cc/$it)!" if $cc;
				next RECORD;
			}

			print STDERR "Setting realTimes{$ns}{$iL}{$cc}{$it} = $time;\n" if $debug>2;
			$realTimes{$ns}{$iL}{$cc}{$it} = $time;
			die "Missing key!" unless exists $realTimes{$ns}{$iL}{$cc}{$it};

			printf STDERR "==== ns: $ns, iL: $iL, it: $it, cc: $cc, time: %f\n", $time if $debug>2;
		}
	}

	foreach my $key(@keys) {
		my ($ns, $iL, $it, $cc) = @$key;

        next if $cc <= 0;

		print STDERR "Keys of realTimes{$ns}{$iL} = \n\t",(join "\n\t", sort keys %{$realTimes{$ns}{$iL}}),"\n" if $debug>2;
		#my $ratio = ($realTimes{$ns}{$iL}{$cc}{$it}
		#             - $realTimes{$ns}{$iL}{-$cc}{$it})
		#           / $costOf0Shuffles;

		# New Ratio will be (+$cc time - 0 shuffle avg time)/(-$cc time - 0 shuffle avg time)
		my $ratio = ($realTimes{$ns}{$iL}{$cc}{$it} - $realTimes{$ns}{$iL}{0}{$it})
		          / ($realTimes{$ns}{$iL}{-$cc}{$it} - $realTimes{$ns}{$iL}{0}{$it});

        printf STDERR "ns: $ns, iL: $iL, cc: $cc, it: $it, +time: %s, -time: %s, 0time: %s, ratio: %s\n",
        									$realTimes{$ns}{$iL}{$cc}{$it},
        									$realTimes{$ns}{$iL}{-$cc}{$it},
        									$realTimes{$ns}{$iL}{0}{$it},
        									$ratio if $debug;

        printf "$ns, $cc, %s\n", $ratio;

        if ($ratio<-1 || $ratio>25) {
            print STDERR "Ratio $ratio for $ns, $iL, $it is strange!\n"
	    }
	}
}

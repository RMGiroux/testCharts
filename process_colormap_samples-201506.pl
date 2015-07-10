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

sub min {
	return $_[0] if $_[0]<$_[1];
	return $_[1];
}

sub max {
	return $_[0] if $_[0]>$_[1];
	return $_[1];
}

if (@ARGV) {
	chdir $ARGV[0] or die "Unable to cd to $ARGV[0], error $!";
}

my $maxDelta = 0;
my @maxDeltaByLog=(-9999)x50;

my %timeFormatREs = (
	"real"     => qr/real\s+(\d+)m(.*?)s/
  , "elapsed"  => qr/(\d+):(\d+\.\d+)elapsed/
);

for my $infile(<oz*>) {
	# Everything below 15 is noise - JSL
	# oz15 has 0's, use 16 as lower bound - RMG
	next unless $infile ge "oz16";

	print STDERR "Processing $infile\n";
	local $/;

	my %realTimes;  # Keys: {ns}{iL}{cc}{it}
	my @baseRealTimes;
	my $averageRealTime = -9999;

	my %seenKeys;
	my @keys;
	my %lines;

	my $prevKey = "";

	open(my $in, "<", $infile) or die "Can't open $infile, error $!";
	local $/;
	local $_ = <$in>;

	my $timeRE = $timeFormatREs{real};

	if(/elapsed/) {
		$timeRE = $timeFormatREs{elapsed};
	}

	while (m{^nS = -(\d+)\s+iL = (\d+)\s+aC = (\d+).*?cC = (-?\d+)\s+it = (\d+).*?$timeRE.*?$}msg) {
		my ($ns, $iL, $aC, $cc, $it, $minutes, $seconds) = ($1, $2, $3, $4, $5, $6, $7);

		my $time = $minutes*60+$seconds;

		my $lineKey = "$ns/$iL/$it";
		my $key = "$ns/$iL/$it/$aC";

		push @keys, [$ns, $iL, $it, $aC, $lineKey] if !$seenKeys{$key}++;

		push @{$lines{$lineKey}}, $&."\n\n";

		die "Reused key!" if exists $realTimes{$ns}{$iL}{$cc}{$it}{$aC};
		$realTimes{$ns}{$iL}{$cc}{$it}{$aC} = $time;
		die "Missing key!" unless exists $realTimes{$ns}{$iL}{$cc}{$it}{$aC};

		#printf "==== $ns, $iL, $aC, $it, $cc, %f\n", $time;
	}

	foreach my $key(@keys) {
		my ($ns, $iL, $it, $aC, $keyStr) = @$key;

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

			my $complaints = 0;

			if ($baseTimeDelta>0.02) {
				printf STDERR "++++++++++ Base times for $ns/$iL/$it ($realTimes{$ns}{$iL}{-5}{$it}{0}, "
						   . "$realTimes{$ns}{$iL}{5}{$it}{0}) differ by more than 2%% (%f %%)\n",
						   $baseTimeDelta * 100 ;
				++$complaints;
			}

			my $logOfTime = max(int(log($realTimes{$ns}{$iL}{-5}{$it}{0})/log(10)),0);

			if ($baseTimeDelta > $maxDeltaByLog[$logOfTime]) {
				$maxDeltaByLog[$logOfTime]=$baseTimeDelta;
				printf STDERR ">>>>>>>>>> New max delta for log range $logOfTime: %f %%\n",
						      $baseTimeDelta*100;

				++$complaints;
			}
			my $ratio = safeDiv($realTimes{$ns}{$iL}{5}{$it}{$aC} - $averageBaseTime,
			                    $realTimes{$ns}{$iL}{-5}{$it}{$aC} - $averageBaseTime);

			printf "$ns, $iL, $it, %s\n", $ratio;

			if ($ratio<0 || $ratio>15) {
			    print STDERR "********** Ratio $ratio for $ns, $iL, $it is strange!\n";
			    ++$complaints;
			}

			if ($complaints) {
			    printf STDERR "\taverageBaseTime               = %f\n",
			    			  $averageBaseTime;
			    printf STDERR "\tnumerator (pre-subtraction)   = %f\n",
			     			  $realTimes{$ns}{$iL}{5}{$it}{$aC};
			    printf STDERR "\tdenominator (pre-subtraction) = %f\n",
			     			  $realTimes{$ns}{$iL}{-5}{$it}{$aC};
			    printf STDERR "\tratio                         = %f\n",
			     			  $ratio;
			    print STDERR @{$lines{$keyStr}},"\n";
			    print STDERR "-"x50,"\n\n";
			}
	    }
	}
}

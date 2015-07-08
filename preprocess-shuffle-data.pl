#!/usr/bin/env perl

use strict;
use warnings;

sub average {
	my $count = @_;
	my $sum   = 0;

	$sum += $_ foreach @_;

	$sum /= $count if $count;

	return $sum;
}

$|++;

my $debug = 1;

my @dirs = <*>;

#my $outputDir = shift @ARGV;

print STDERR "Reading from [@dirs]\n";

my @filenames;

do {
    chdir "$dirs[0]";
    @filenames=<*>;
    chdir "..";
};

print STDERR "- list of files: [@filenames]\n";

my %seenKeys;
my @keys;
my %realTimes;

local $/;
$/ = "swaps\n";

my $prevKey = "";

foreach my $file(@filenames) {
    foreach my $dir(@dirs) {
        my $infile = "$dir/$file";
        print STDERR "-- processing $infile\n";

        open(my $in, "<", $infile) or die "Can't open $infile, error $!";

        RECORD: while(<$in>) {
            if (m{^nS = (\d+)\s+iL = (\d+).*?aC = (\d+)\s+cC = (-?\d+)\s+it = (\d+).*?(\d+):(\d+\.\d+)elapsed.*?$}ms) {
                my ($ns, $iL, $ac, $cc, $it, $minutes, $seconds) = ($1, $2, $3, $4/10000000, $5, $6, $7);

                #next RECORD if $ac == 0;

                my $time = $minutes*60+$seconds;

                my $key = "$ns/$iL/$it/$cc/$ac";
                print STDERR "===  $key, $time\n";

                push @keys, [$ns, $iL, $it, $cc, $ac] if !$seenKeys{$key}++;

                print STDERR "Adding $time to realTimes{$ns}{$iL}{$cc}{$it}{$ac}\n" if $debug>2;
                push @{$realTimes{$ns}{$iL}{$cc}{$it}{$ac}}, $time;

                printf STDERR "==== file: $infile, ns: $ns, iL: $iL, it: $it, cc: $cc, ac: $ac, time: %f\n", $time if $debug;
            }
        }

        close($in) or die "Error closing $infile, erorr $!";
    }
}

my $maxSpread = 0;
my $maxLine;

print "#ns, iL, it, cc, ac, [ times ], spread, minTime\n";

foreach my $key (@keys) {
    my ($ns, $iL, $it, $cc, $ac) = @$key;

    my @times = sort {$a <=> $b} @{$realTimes{$ns}{$iL}{$cc}{$it}{$ac}};

    die "Not enough times for @$key" unless @times == @dirs;

    my $spread = ($times[4]-$times[0])/$times[0] * 100;
    #my $average = average(@times[0..4]);
    my $min = $times[0];

    my $line = sprintf "$ns, $iL, $it, $cc, $ac, [ @times ], %f, %.6f\n", $spread, $min;
    print "$line";

    if ($spread > $maxSpread) {
        $maxSpread=$spread;
        $maxLine = $line;
    }
}

print STDERR "Max spread is $maxSpread (for $maxLine)\n" if $debug;
import numpy as np
import sys
import os
import re

import graphSupport

# http://stackoverflow.com/questions/635483/what-is-the-best-way-to-implement-nested-dictionaries-in-python/19829714#19829714
class Vividict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


# Tell NumPy to print all of each array rather than eliding some...
np.set_printoptions(threshold=np.nan)

def processTestData(file, subheading, outdir, iteration_factor=1):
    values = Vividict()

    try:
        os.mkdir(outdir)
    except OSError:
        # ignore it if the directory already exists
        pass

    with open(file) as f:
        for line in f:
            line = re.sub(r"\s*#.*", '', line)

            if re.search(',', line):
                fields = line.split(",")
                values[int(fields[0])][int(fields[1])][int(fields[2])] \
                    = fields[3]

    print "values are ", values

    for dataset in values.keys():
        #if dataset not in range(21, 25):
        #    continue

        X = range(0, 9)
        Y = values[dataset].keys()


        print "X is ", X
        print "Y is ", Y

        mat = np.zeros([len(Y), len(X)])

        try:
            for x in X:
                for y in Y:
                    mat[y, x] = values[dataset][y][iteration_factor * 2 ** x]
        except:
            print "***** Error (%s: %s) for dataset %s" % (sys.exc_info()[0], sys.exc_info()[1], dataset)

        print "mat is ", mat

        for factorArg in (15, ):
            for cmap in ('jet', ):
                print "Plotting dataset %d at factor %d (colormap %s) (for %s)" % (dataset, factorArg, cmap, subheading)
                graphSupport.output_plot_and_table(X,
                                                   Y,
                                                   mat,
                                                   "Problem Size = $2^{%d}$\n%s" % (dataset, subheading),
                                                   "Temporal Locality",
                                                   [0, 1, 2, 3, 4, 5, 6, 7, 8],
                                                   ['$2^{-%d}$' % i for i in range(0, 9)],
                                                   ['2^-%d' % i for i in range(0, 9)],
                                                   "lg(Subsystem Size)",
                                                   Y,
                                                   [int(i) for i in Y],
                                                   [int(i) for i in Y],
                                                   "%s/foo_%02d_%d_%s.png" % (outdir,dataset, factorArg, cmap),
                                                   "%s/foo_%02d_table.png" % (outdir,dataset),
                                                   "%s/foo_%02d_table.csv" % (outdir,dataset),
                                                   factor=factorArg,
                                                   colormap=cmap)

def processSuffledData():
    values = Vividict()

    filename = "processed_shuffle_data.out"
    #filename = "processed_shuffle_test_data.out"

    with open(filename) as f:
        for line in f:
            line = re.sub(r"\s*#.*", '', line)

            if re.search(',', line):
                fields = line.split(",")
                # x is ns - we want system size TODO: using 9 - is a big hack here to switch from ns to system size
                x = 9 - len(str(fields[0]))
                # print "values[%d][%d] = %s" % (x, int(fields[1]), fields[2])
                # y is shuffle count
                values[x][int(fields[1])] = fields[2]

    X = values.keys()
    Y = values[1].keys()
    mat = np.zeros([len(Y), len(X)])

    print "X is ", X
    print "Y is ", Y

    try:
        for x in range(0, len(X)):
            for y in Y:
                value = float(values[X[x]][y])
                print "x: %d, y: %d, X[x]=%d, value = %f" % (x, y, X[x], value)
                # print "value = %s" % value
                mat[y, x] = value
    except:
        print "***** Error (%s: %s)" % (sys.exc_info()[0], sys.exc_info()[1])

    print "values is ", values
    print "Mat is ", mat

    for factorArg in (20,):
        for cmap in ('jet', ):
            print "Plotting Shuffle Data at factor %d (colormap %s)" % (factorArg, cmap)
            graphSupport.output_plot_and_table(Y,
                                               X,
                                               mat.transpose(),
                                               "Shuffle Effects",
                                               "Shuffle Factor",
                                               Y,
                                               [i for i in range(0, 1 + len(Y))],
                                               [i for i in range(0, 1 + len(Y))],
                                               "Subsystem Size",
                                               X,
                                               ['$10^{%d}$' % i for i in range(0, len(X))],
                                               ['10^%d' % i for i in range(0, len(X))],
                                               "images/shuffle_%d_%s.png" % (factorArg, cmap), # None,
                                               "images/shuffle_table.png",
                                               "images/shuffle_table.csv",
                                               factor=factorArg,
                                               colormap=cmap,
                                               block=True)


try:
    os.mkdir("images")
except OSError:
    # ignore it if the directory already exists
    pass

#processTestData("input-data-10x-20150831/processed_test_data-with-allocators.out", "With Allocators", "images-10x-with-allocators", 10)
#processTestData("input-data-10x-20150831/processed_test_data-without-allocators.out", "Without Allocators", "images-10x-without-allocators", 10)
processTestData("input-data-10x-20150831/processed_data_ratio.out", "Ratio Without/With Allocators", "images-10x-ratio", 10)
#processSuffledData()

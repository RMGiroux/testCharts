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

def processTestData():
    values = Vividict()

    with open("processed_test_data.out") as f:
        for line in f:
            line = re.sub(r"\s*#.*", '', line)

            if re.search(',', line):
                fields = line.split(",")
                values[int(fields[0])][int(fields[1])][int(fields[2])] \
                    = fields[3]

    for dataset in values.keys():
        if dataset not in (21, 25):
            continue

        X = range(0, 9)
        Y = values[dataset].keys()

        mat = np.zeros([len(Y), len(X)])

        try:
            for x in X:
                for y in Y:
                    mat[y, x] = values[dataset][y][2 ** x]
        except:
            print "***** Error (%s: %s) for dataset %s" % (sys.exc_info()[0], sys.exc_info()[1], dataset)


        for factorArg in (15, ):
            for cmap in ('jet', ):
                print "Plotting dataset %d at factor %d (colormap %s)" % (dataset, factorArg, cmap)
                graphSupport.output_plot_and_table(X,
                                                   Y,
                                                   mat,
                                                   "Problem Size = $2^{%d}$" % dataset,
                                                   "Temporal Locality",
                                                   [0, 1, 2, 3, 4, 5, 6, 7, 8],
                                                   ['$2^{-%d}$' % i for i in range(0, 9)],
                                                   ['2^-%d' % i for i in range(0, 9)],
                                                   "Subsystem Size",
                                                   Y,
                                                   ['$2^{%d}$' % int(i) for i in Y],
                                                   ['2^%d' % int(i) for i in Y],
                                                   "images/foo_%02d_%d_%s.png" % (dataset, factorArg, cmap),
                                                   "images/foo_%02d_table.png" % dataset,
                                                   "images/foo_%02d_table.csv" % dataset,
                                                   factor=factorArg,
                                                   colormap=cmap)

def processSuffledData():
    values = Vividict()

    with open("processed_shuffle_data.out") as f:
        for line in f:
            line = re.sub(r"\s*#.*", '', line)

            if re.search(',', line):
                fields = line.split(",")
                x = len(str(fields[0]))
                # print "values[%d][%d] = %s" % (x, int(fields[1]), fields[2])
                values[x][int(fields[1])] = fields[2]

    X = values.keys()
    Y = values[1].keys()
    mat = np.zeros([len(Y), len(X)])

    try:
        for x in range(0, len(X)):
            for y in Y:
                value = float(values[X[x]][y])
                print "x: %d, y: %d, X[x]=%d, value = %f" % (x, y, X[x], value)
                # print "value = %s" % value
                mat[y - 1, x] = value
    except:
        print "***** Error (%s: %s)" % (sys.exc_info()[0], sys.exc_info()[1])


    for factorArg in (15, ):
        for cmap in ('jet', ):
            print "Plotting Shuffle Data at factor %d (colormap %s)" % (factorArg, cmap)
            graphSupport.output_plot_and_table(Y,
                                               X,
                                               (np.flipud(mat.transpose())),#np.fliplr(np.flipud(mat.transpose())),
                                               "Shuffle Effects",
                                               "Shuffle Factor",
                                               Y,
                                               [i for i in range(1, 1 + len(Y))],
                                               [i for i in range(1, 1 + len(Y))],
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

# processTestData()
processSuffledData()
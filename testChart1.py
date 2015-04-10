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

values = Vividict()

try:
    os.mkdir("images")
except OSError:
    # ignore it if the directory already exists
    pass

with open("processed_test_data.out") as f:
    for line in f:
        line = re.sub(r"\s*#.*", '', line)

        if re.search(',', line):
            fields = line.split(",")
            values[int(fields[0])][int(fields[1])][int(fields[2])] \
                = fields[3]

for dataset in values.keys():
    if dataset != 25:
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
                                               "Subsystem Size",
                                               Y,
                                               ['$2^{%d}$' % int(i) for i in Y],
                                               "images/foo_%02d_%d_%s.png" % (dataset, factorArg, cmap),
                                               "images/foo_%02d_table.png" % dataset,
                                               factor=factorArg,
                                               colormap=cmap)

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import sys

# http://stackoverflow.com/questions/635483/what-is-the-best-way-to-implement-nested-dictionaries-in-python/19829714#19829714
class Vividict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

values = Vividict()

with open("processed_test_data.out") as f:
    for line in f:
        fields = line.split(",")
        values[int(fields[0])][int(fields[1])][int(fields[2])]\
            = fields[3]

for dataset in values.keys():
    print "D: %s" % dataset

    try:
        X = range(0, 9)
        Y = values[dataset].keys()

        mat = np.zeros([len(Y), len(X)])

        for x in X:
            for y in Y:
                mat[y, x] = values[dataset][y][2**x]

        #print "X = ",X
        #print "Y = ",Y
        #print "mat = ",mat

        X, Y = np.meshgrid(X, Y)

        fig = plt.figure()
        ax = fig.add_subplot(1,1,1, projection='3d')

        fig.suptitle("Data run %d" % dataset)

        ax.set_xticks([0, 1, 2, 3, 4, 5, 6, 7, 8])
        ax.set_xticklabels(['1', '2', '4', '8', '16', '32', '64', '128', '256'])

        surf = ax.plot_surface(X,
                               Y,
                               mat,
                               cmap=cm.Blues,
                               linewidth=0,
                               rstride=1, cstride=1,
                               )

        plt.savefig("images/foo_%03d.png" % dataset, bbox_inches='tight')
    except:
        print "***** Error (%s: %s) for dataset %s" % (sys.exc_info()[0], sys.exc_info()[1], dataset)
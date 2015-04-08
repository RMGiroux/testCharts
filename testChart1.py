from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import sys
import os

def linearInterp1DintoTarget(target, source, factor=5):
    """Interpolates the 'source' vector linearly into the 'target' vector, piece-wise,
       inserting 'factor' interpolated elements between each of the 'source' elements.

    :rtype : vector

       Requires: 'len(target) == (len(source) + factor * (len(source) - 1))'
    """

    assert len(target) == (1 + factor * (len(source) - 1))

    for i in range(0, len(source) - 1):
        tIdx = i * factor
        delta = (source[i + 1] - source[i]) / (1.0 * factor)

        target[tIdx] = source[i]

        for j in range(0, factor):
            target[tIdx + j] = source[i] + (j * delta)

    target[-1] = source[-1]

    return target


def linearInterp1D(source, factor=5):
    target = np.zeros(1 + (len(source) - 1) * factor)

    return linearInterp1DintoTarget(target, source, factor)


def linearInterp2D(source, factor=5):
    """

    :param source:
    :param factor:
    :return: np.ndarray
    """
    sShape = source.shape
    rXShape = 1 + factor * (sShape[0] - 1)
    rYShape = 1 + factor * (sShape[1] - 1)
    target = np.zeros([rXShape, rYShape])

    for i in range(0, sShape[0]):
        tXIdx = i * factor

        linearInterp1DintoTarget(target[tXIdx], source[i])

    linearInterp1DintoTarget(target[-1], source[-1])

    for i in range(0, sShape[0] - 1):
        tXIdx = i * factor

        deltas = np.zeros(rYShape)

        for j in range(0, rYShape):
            deltas[j] = (target[tXIdx + factor][j] - target[tXIdx][j]) / factor

        for x in range(0, factor):
            for y in range(0, rYShape):
                target[tXIdx + x][y] = target[tXIdx][y] + x * deltas[y]

    return target


# http://stackoverflow.com/questions/635483/what-is-the-best-way-to-implement-nested-dictionaries-in-python/19829714#19829714
class Vividict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


values = Vividict()

try:
    os.mkdir("images")
except OSError:
    # ignore it if the directory already exists
    pass

with open("processed_test_data.out") as f:
    for line in f:
        fields = line.split(",")
        values[int(fields[0])][int(fields[1])][int(fields[2])] \
            = fields[3]

for dataset in values.keys():
    print "D: %s" % dataset

    X = range(0, 9)
    Y = values[dataset].keys()

    Xinterp = linearInterp1D(X)
    Yinterp = linearInterp1D(Y)

    mat = np.zeros([len(Y), len(X)])

    try:
        for x in X:
            for y in Y:
                mat[y, x] = values[dataset][y][2 ** x]
    except:
        print "***** Error (%s: %s) for dataset %s" % (sys.exc_info()[0], sys.exc_info()[1], dataset)

    newMat = linearInterp2D(mat)

    np.set_printoptions(threshold=np.nan)

    # print "Xinterp = ", Xinterp
    # print "Yinterp = ", Yinterp
    # print "mat = ", mat
    # print "newMapt = ", newMat

    # print "X = ",X
    # print "Y = ",Y
    # print "mat = ",mat

    fig = plt.figure()
    fig.suptitle("Problem Size = $2^{%d}$" % dataset)

    ax = fig.add_subplot(1, 1, 1, projection='3d')

    ax.set_xlabel("Temporal Locality", fontsize=8)
    ax.set_xticks([0, 1, 2, 3, 4, 5, 6, 7, 8])
    ax.set_xticklabels(['$2^{%d}$' % i for i in range(0, 9)])

    ax.set_ylabel("Subsystem Size", fontsize=8)
    ax.set_yticks(Y)
    ax.set_yticklabels(['$2^{%d}$' % int(i) for i in Y])

    ax.tick_params(axis='both', which='major', labelsize=7)
    ax.tick_params(axis='both', which='minor', labelsize=7)

    #ax.text(3, 8, 'boxed italics text in data coords $2^20$', style='italic', bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})

    Xinterp, Yinterp = np.meshgrid(Xinterp, Yinterp)

    surf = ax.plot_surface(Xinterp,
                           Yinterp,
                           newMat,
                           cmap=cm.Blues,
                           linewidth=0,
                           rstride=1, cstride=1,
                           )

    #plt.show()
    plt.savefig("images/foo_%03d.png" % dataset, bbox_inches='tight', pad_inches=0.25)

    sys.exit(0)

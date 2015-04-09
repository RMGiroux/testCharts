from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import sys
import os
import re

def linearInterp1DintoTarget(target, source, factor=5):
    """Interpolates the 'source' vector linearly into the 'target' vector, piece-wise,
       inserting 'factor' interpolated elements between each of the 'source' elements.

    :param target: "Expanded" vector into which interpolated values will be placed
    :param source: Vector to expand
    :param factor: Expansion factor
    :return: np.ndarray

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
    """Returns a vector expanding on 'source' by inserting 'factor' linearly-interpolated values in between each
    entry.

    :param source: Vector to be expanded
    :param factor: Expansion factor
    :return: np.ndarray
    """

    if factor == 0:
        return source

    target = np.zeros(1 + (len(source) - 1) * factor)

    return linearInterp1DintoTarget(target, source, factor)


def linearInterp2D(source, factor=5):
    """Returns a matrix expanding on 'source' by inserting 'factor' linearly-interpolated values
    in between each entry in both dimensions.

    :param source: Matrix to be expanded
    :param factor: Expansion factor
    :return: np.ndarray
    """

    if factor == 0:
        return source

    sShape = source.shape
    rXShape = 1 + factor * (sShape[0] - 1)
    rYShape = 1 + factor * (sShape[1] - 1)
    target = np.zeros([rXShape, rYShape])

    for i in range(0, sShape[0]):
        tXIdx = i * factor

        linearInterp1DintoTarget(target[tXIdx], source[i], factor)

    linearInterp1DintoTarget(target[-1], source[-1], factor)

    for i in range(0, sShape[0] - 1):
        tXIdx = i * factor

        deltas = np.zeros(rYShape)

        for j in range(0, rYShape):
            deltas[j] = (target[tXIdx + factor][j] - target[tXIdx][j]) / factor

        for x in range(0, factor):
            for y in range(0, rYShape):
                target[tXIdx + x][y] = target[tXIdx][y] + x * deltas[y]

    return target

def plot_graph(X, Y, Z, filename, factor=0, block=False):
    """
    Plot a 3D surface for X, Y, and Z, interpolating the data by 'factor' if specified.

    If 'filename' is not None, then save the result into 'filename'.  Otherwise, display
    the graphic interactively, blocking if 'block' is True.

    :param X: the X axis points (1 dimensional np.ndarray)
    :param Y: the Y axis points (1 dimensional np.ndarray)
    :param Z: the Z axis points (2 dimensional np.ndarray)
    :param filename: The filename to save into, or, if None, then indicates graph should be displayed
    :param factor: Interpolation factor, in order to add polygons to graph and improve appearance without altering shape
    :param block: Whether or not to block in interactive mode
    :return: None
    """

    fig = plt.figure()
    fig.suptitle("Problem Size = $2^{%d}$" % dataset)

    ax = fig.add_subplot(1, 1, 1, projection='3d')

    ax.set_xlabel("Temporal Locality", fontsize=8)
    ax.set_xticks([0, 1, 2, 3, 4, 5, 6, 7, 8])
    ax.set_xticklabels(['$2^{-%d}$' % i for i in range(0, 9)])

    ax.set_ylabel("Subsystem Size", fontsize=8)
    ax.set_yticks(Y)
    ax.set_yticklabels(['$2^{%d}$' % int(i) for i in Y])

    ax.tick_params(axis='both', which='major', labelsize=7)
    ax.tick_params(axis='both', which='minor', labelsize=7)

    Xinterp = linearInterp1D(X, factor)
    Yinterp = linearInterp1D(Y, factor)
    Zinterp = linearInterp2D(Z, factor)

    Xinterp, Yinterp = np.meshgrid(Xinterp, Yinterp)

    surf = ax.plot_surface(Xinterp,
                           Yinterp,
                           Zinterp,
                           cmap=cm.BuPu,
                           linewidth=0,
                           rstride=1, cstride=1,
                           )

    if filename is None:
        plt.show(block)

        # If block is true, then we we can close the figure(s) after the user is done interacting.
        if block:
            plt.close(fig)
    else:
        plt.savefig(filename, bbox_inches='tight', pad_inches=0.25)
        plt.close(fig)


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
        line = re.sub(r"\s*#.*", '', line)

        if re.search(',', line):
            fields = line.split(",")
            values[int(fields[0])][int(fields[1])][int(fields[2])] \
                = fields[3]

for dataset in values.keys():
    print "D: %s" % dataset

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

    # Tell NumPy to print all of each array rather than eliding some...
    np.set_printoptions(threshold=np.nan)

    factorArg = 6

    # Set to False for interactive examination of graphs
    if True:
        plot_graph(X, Y, mat, "images/foo_%02d_0.png" % dataset, factor=0)
        plot_graph(X, Y, mat, "images/foo_%02d_%d.png" % (dataset, factorArg), factor=factorArg)
    else:
        plot_graph(X, Y, mat, None, factor=0, block=False)
        plot_graph(X, Y, mat, None, factor=factorArg, block=True)

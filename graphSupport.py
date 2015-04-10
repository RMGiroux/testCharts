from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

# The full list of available colormaps (for testing, not needed at the moment).
cmaps = ('Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd',
                             'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu',
                             'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd',
         'afmhot', 'autumn', 'bone', 'cool', 'copper',
                             'gist_heat', 'gray', 'hot', 'pink',
                             'spring', 'summer', 'winter',
         'BrBG', 'bwr', 'coolwarm', 'PiYG', 'PRGn', 'PuOr',
                             'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral',
                             'seismic',
         'Accent', 'Dark2', 'Paired', 'Pastel1',
                             'Pastel2', 'Set1', 'Set2', 'Set3',
         'gist_earth', 'terrain', 'ocean', 'gist_stern',
                             'brg', 'CMRmap', 'cubehelix',
                             'gnuplot', 'gnuplot2', 'gist_ncar',
                             'nipy_spectral', 'jet', 'rainbow',
                             'gist_rainbow', 'hsv', 'flag', 'prism')



def linearInterp1DintoTarget(target, source, factor=5):
    """Interpolates the 'source' vector linearly into the 'target' vector, piece-wise,
       inserting 'factor' interpolated elements between each of the 'source' elements.

       Examples:
          source:
             [ 1., 2., 3. ]

          factor 3:  [ 1., 1.33333333, 1.66666667, 2., 2.33333333, 2.66666667, 3. ]

          factor 5:  [ 1., 1.2, 1.4, 1.6, 1.8, 2., 2.2, 2.4, 2.6, 2.8, 3. ]

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

def output_csv(X, xCSVLabels, Y, yCSVLabels, Z, tableCsvFilename):

    def quote(s):
        return "\"%s\"" % s

    if tableCsvFilename is not None:
        with open(tableCsvFilename, "w") as f:
            f.write(",%s\n" % ",".join(map(quote, xCSVLabels)))
            for rowIndex in range(0, len(Y)):
                f.write("\"%s\"" % yCSVLabels[rowIndex])
                for colIndex in range(0, len(X)):
                    # f.write(",%f" % Z[len(Y) - rowIndex - 1][colIndex])
                    f.write(",%f" % Z[rowIndex][colIndex])
                f.write("\n")

def output_plot_and_table(X, Y, Z,
               title,
               xTitle, xTicks, xLabels, xCSVLabels,
               yTitle, yTicks, yLabels, yCSVLabels,
               filename,
               tablePngFilename,
               tableCsvFilename,
               factor=0, block=False, colormap = "jet"):
    """
    Plot a 3D surface for X, Y, and Z, interpolating the data by 'factor' if specified,
    and output a graphical tabular version of the data as well.

    If 'filename' is not None, then save the result into 'filename'.  Otherwise, display
    the graphic interactively, blocking if 'block' is True.

    :param X: the X axis points (1 dimensional np.ndarray)
    :param Y: the Y axis points (1 dimensional np.ndarray)
    :param Z: the Z axis points (2 dimensional np.ndarray)
    :param title: the graph title
    :param xTitle: the X axis title
    :param xTicks: the X axis numerical ticks
    :param xLabels: the X axis labels
    :param xCSVLabels: the X axis labels (CSV format)
    :param yTitle: the Y axis title
    :param yTicks: the Y axis numerical ticks
    :param yLabels: the Y axis labels
    :param yCSVLabels: the Y axis labels (CSV format)
    :param filename: The filename to save into, or, if None, then indicates graph should be displayed
    :param tablePngFilename: the filename to save the table graphic into
    :param tableCsvFilename: the filename to save the table csv into
    :param factor: Interpolation factor, in order to add polygons to graph and improve appearance without altering shape
    :param block: Whether or not to block in interactive mode
    :return: None
    """

    fig = plt.figure()
    fig.suptitle(title)

    ax = fig.add_subplot(1, 1, 1, projection='3d')

    ax.set_xlabel(xTitle, fontsize=8)
    ax.set_xticks(xTicks)
    ax.set_xticklabels(xLabels)

    ax.set_ylabel(yTitle, fontsize=8)
    ax.set_yticks(yTicks)
    ax.set_yticklabels(yLabels)

    ax.tick_params(axis='both', which='major', labelsize=7)
    ax.tick_params(axis='both', which='minor', labelsize=7)

    Xinterp = linearInterp1D(X, factor)
    Yinterp = linearInterp1D(Y, factor)
    Zinterp = linearInterp2D(Z, factor)

    Xinterp, Yinterp = np.meshgrid(Xinterp, Yinterp)

    surf = ax.plot_surface(Xinterp,
                           Yinterp,
                           Zinterp,
                           cmap=plt.get_cmap(colormap),
                           linewidth=0,
                           rstride=1, cstride=1,
                           alpha=1.0
                           )

    if filename is None:
        plt.show(block)

        # If block is true, then we we can close the figure(s) after the user is done interacting.
        if block:
            plt.close(fig)
    else:
        plt.savefig(filename, bbox_inches='tight', pad_inches=0.25)
        plt.close(fig)

    # if tablePngFilename is not None:
    #     hcell, wcell = 0.125, 4.
    #     hpad, wpad = 0, 0
    #     nrows, ncols = len(yLabels) + 1, len(xLabels)
    #     fig=plt.figure(figsize=(ncols*wcell+wpad, nrows*hcell+hpad),dpi=600)
    #     ax=fig.add_subplot('111')
    #     ax.axis('off')
    #
    #     if len(xLabels) > len(yLabels):
    #         table = ax.table(cellText=Z.transpose(),
    #                          rowLabels=xLabels,
    #                          colLabels=yLabels,
    #                          loc='center')
    #     else:
    #         table = ax.table(cellText=Z,
    #                          rowLabels=yLabels,
    #                          colLabels=xLabels,
    #                          loc='center')
    #
    #     table_props = table.properties()
    #     table_cells = table_props['child_artists']
    #     for cell in table_cells:
    #         cell.set_height(0.25)
    #
    #     plt.savefig(tablePngFilename, bbox_inches='tight')
    #     plt.close(fig)


    if len(X) <= len(Y):
        output_csv(X, xCSVLabels, Y, yCSVLabels, Z, tableCsvFilename)
    else:
        output_csv(Y, yCSVLabels, X, xCSVLabels, Z.transpose(), tableCsvFilename)

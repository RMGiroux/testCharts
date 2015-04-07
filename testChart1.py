from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

bignum = 4
#mat = np.random.random((bignum, bignum))
mat = [[1,2,3,4],
       [2,3,4,5],
       [3,4,5,6],
       [4,5,6,5]]
X, Y = np.mgrid[:bignum, :bignum]

print "X:\n",X
print "Y:\n",Y
print "mat:\n",mat

fig = plt.figure()
ax = fig.add_subplot(1,1,1, projection='3d')
surf = ax.plot_surface(X,Y,mat)
#ax.set_xscale('log', basex=2)
plt.show()
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

bignum = 4
mat = np.random.random((bignum, bignum))
X, Y = np.mgrid[:bignum, :bignum]

print "X:\n",X
print "Y:\n",Y
print "mat:\n",mat

fig = plt.figure()
ax = fig.add_subplot(1,1,1, projection='3d')
surf = ax.plot_surface(X,Y,mat)
plt.show()
import numpy as np
from sklearn.preprocessing import normalize
import pyqtgraph as pg
from pyqtgraph import opengl as gl
from pyqtgraph.Qt import QtGui


file_name = 'VoxelFaces/32^3/bs000_CAU_A22A25_0.bnt.abs.obj.txt'
size=100
x_voxel = np.loadtxt(file_name).astype(np.int64)
print('shape of voxel:  ', x_voxel.shape)
[x_min, y_min, z_min] = np.amin(x_voxel, axis=0)
[x_max, y_max, z_max] = np.amax(x_voxel, axis=0)

x_len = x_max + abs(x_min) + 1
y_len = y_max + abs(y_min) + 1
z_len = z_max + abs(z_min) + 1

print('size of voxel:  ', x_len, y_len, z_len)
file_refined=x_voxel
print(file_refined.shape)
for i in range(file_refined.shape[0]):
    file_refined[i][0] = size*(file_refined[i][0] - x_min) / (x_max - x_min)
    file_refined[i][1] = size*(file_refined[i][1] - y_min) / (y_max - y_min)
    file_refined[i][2] = size*(file_refined[i][2] - z_min) / (z_max - z_min)

x_voxel=file_refined
[x_min, y_min, z_min] = np.amin(x_voxel, axis=0)
[x_max, y_max, z_max] = np.amax(x_voxel, axis=0)
print(x_min, y_min, z_min)
print(x_max, y_max, z_max)
# converting voxel into 3d numpy array
voxel_binary = np.zeros(shape=(size+1, size+1, size+1))
for i in range(x_voxel.shape[0]):
    voxel_binary[int(x_voxel[i][0]) + abs(x_min)][int(x_voxel[i][1]) + abs(y_min)][int(x_voxel[i][2]) + abs(z_min)] = 1


np.save('voxel', voxel_binary)
# for plotting
app = QtGui.QApplication([])
pg.setConfigOption('background', 'w')
w = gl.GLViewWidget()
w.show()
w.setWindowTitle('pyqtgraph example: GLScatterPlotItem')
g = gl.GLAxisItem()
g.setSize(x=500, y=500, z=500)
w.addItem(g)

plot = gl.GLScatterPlotItem()
plot.setData(pos=x_voxel, size=1.5)
w.addItem(plot)
w.show()
QtGui.QApplication.instance().exec_()

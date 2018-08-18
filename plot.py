import numpy as np
import math
from sklearn.preprocessing import normalize
import pyqtgraph as pg
from pyqtgraph import opengl as gl
from pyqtgraph.Qt import QtGui


file_name='Bosphorus/bs003/bs003_CR_RD_0.bnt.npy'


def rotate(arr, angle=math.radians(-80)):
    cos = math.cos(angle)
    sin = math.sin(angle)
    x = arr[2]*sin + arr[0]*cos
    z = arr[2]*cos - arr[0]*sin
    return np.asanyarray([x, arr[1], z])


file = np.load(file_name)

file_refined=[]
for i in range(file.shape[1]):
    if(file[0][i]):
        file_refined.append([file[1][i], file[2][i], file[3][i]])

file_final = np.asanyarray(file_refined).astype(np.float64)
np.save('example',file_final)
app = QtGui.QApplication([])
pg.setConfigOption('background', 'w')
w = gl.GLViewWidget()
w.show()
w.setWindowTitle('pyqtgraph example: GLScatterPlotItem')
g = gl.GLAxisItem()
g.setSize(x=500, y=500, z=500)
w.addItem(g)

plot = gl.GLScatterPlotItem()
plot.setData(pos=normalize(np.asanyarray(file_final).astype(np.float64), axis=0), size=1.5)
w.addItem(plot)
w.show()
QtGui.QApplication.instance().exec_()
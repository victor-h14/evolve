from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np

app = QtGui.QApplication([])
view = gl.GLViewWidget()
view.opts['distance'] = 20
view.show()
side = 30
      
                  
random = np.random.random((side, side))
mountain = np.cos(np.arange(side**2)*np.pi/5).reshape(side, side)
heights = mountain + random

dots = np.zeros((side**2, 3))
color = np.ones((side**2, 4))*0.8
size = np.ones(side**2)*0.1
face1 = []
face2 = []

for i in range(side):
    for j in range(side):
        dots[side*i + j] = (i-side/2, j-side/2, heights[i, j])

for i in range(side-1):
    for j in range(side-1):
        face1.append([side*i+j, side*i+j+1,side*(i+1)+j])
        face2.append([side*(i+1)+j+1, side*i+j+1,side*(i+1)+j])

faces = np.array(face1 + face2)
faceColors = np.ones(faces.shape)*0.5
mesh = gl.GLMeshItem(meshdata=gl.MeshData(vertexes=dots, faces=faces, faceColors=faceColors))
mesh.setGLOptions(opts="translucent")
view.addItem(mesh)

scatter_plot = gl.GLScatterPlotItem()
scatter_plot.setData(pos=dots, size=size, color=color, pxMode=False)
view.addItem(scatter_plot)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


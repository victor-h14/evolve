from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np

app = QtGui.QApplication([])
view = gl.GLViewWidget()
view.opts['distance'] = 20
view.show()

grid = gl.GLGridItem()
view.addItem(grid)

dim = 2
pos = np.empty((dim, 3))
size = np.ones(dim)
color = np.ones((dim, 4))
scatter_plot = gl.GLScatterPlotItem(pos=pos, size=size, color=color, pxMode=False)
view.addItem(scatter_plot)


def update():
    ## update surface positions and colors
    global scatter_plot, pos
    step = np.zeros((dim, 3))
    for i in range(dim):
        step[i, 0] = np.random.random() - 0.5
        step[i, 1] = np.random.random() - 0.5
    pos += step
    print(pos)
    scatter_plot.setData(pos=pos, color=color)
    
t = QtCore.QTimer()
t.timeout.connect(update)
t.start(50)


## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np

app = QtGui.QApplication([])
view = gl.GLViewWidget()
view.opts['distance'] = 20
view.show()
view.resize(1000,1000)
dim = 20

grid = gl.GLGridItem()
view.addItem(grid)

map1 = [["" for j in range(dim)] for i in range(dim)]
ind1 = []
pos = np.zeros((dim**2, 3))
for i in range(dim):
    for j in range(dim):
        pos[i*dim + j] = (i -(dim-1)/2, j -(dim-1)/2, 0)

size = np.ones(dim**2)*0.5
color = np.zeros((dim**2, 4))
scatter_plot = gl.GLScatterPlotItem(pos=pos, size=size, color=color, pxMode=False)
view.addItem(scatter_plot)

map1[0][0] = "A;A"
ind1.append(0)

def update():
    global scatter_plot, pos, color, ind1
    for i in range(dim):
        for j in range(dim):
            if(map1[i][j] == "A;A"):
                color[i*dim + j] = (0, 1, 0, 1)
    scatter_plot.setData(color=color)
    
    temp = []
    for index in ind1:
        j = index % dim
        i = (index - j) // dim
        r = np.random.randint(4)
        
        if(r==0 and i != dim-1):
            if(index + dim not in ind1):
                temp.append(index + dim)
                map1[i+1][j] = "A;A"
                
        elif(r==1 and i != 0):
            if(index - dim not in ind1):
                temp.append(index - dim)
                map1[i-1][j] = "A;A"
                
        elif(r==2 and j != dim-1):
            if(index + 1 not in ind1):
                temp.append(index + 1)
                map1[i][j+1] = "A;A"
                
        elif(r==3 and j != 0):
            if(index - 1 not in ind1):
                temp.append(index - 1)
                map1[i][j-1] = "A;A"
                
    ind1 = ind1 + temp
    
t = QtCore.QTimer()
t.timeout.connect(update)
t.start(500)


## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


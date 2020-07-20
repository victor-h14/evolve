from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import parametertree as pt
import pyqtgraph.opengl as gl
import numpy as np

class Window(object):
    def setupUi(self, mainWindow):
        self.mainWindow = mainWindow
        self.mainWindow.setObjectName("Player")

        ### view
        self.view = gl.GLViewWidget()
        self.view.opts['distance'] = 150
        self.mainWindow.setCentralWidget(self.view)

        ### timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)

        ### toolbar
        self.toolBar = QtGui.QToolBar(self.mainWindow)
        self.mainWindow.addToolBar(self.toolBar)

        ### dock widget
        self.dockParameterTree = QtGui.QDockWidget(self.mainWindow)
        self.mainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.dockParameterTree)

        ### parameter tree
        self.parameterTree = pt.ParameterTree(self.dockParameterTree)
        self.dockParameterTree.setWidget(self.parameterTree)
        self.dockParameterTree.setVisible(False)

        ### buttons
        self.restartButton = QtGui.QAction(self.mainWindow)
        self.restartButton.triggered.connect(self.restart)
        iconRestart = QtGui.QIcon()
        iconRestart.addPixmap(QtGui.QPixmap("images/restart.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.restartButton.setIcon(iconRestart)
        self.toolBar.addAction(self.restartButton)

        self.slowerButton = QtGui.QAction(self.mainWindow)
        self.slowerButton.triggered.connect(lambda: self.timer.start(1250))
        iconSlower = QtGui.QIcon()
        iconSlower.addPixmap(QtGui.QPixmap("images/slower.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.slowerButton.setIcon(iconSlower)
        self.toolBar.addAction(self.slowerButton)

        self.playButton = QtGui.QAction(self.mainWindow)
        self.playButton.triggered.connect(lambda: self.timer.start(250))
        iconPlay = QtGui.QIcon()
        iconPlay.addPixmap(QtGui.QPixmap("images/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.playButton.setIcon(iconPlay)
        self.toolBar.addAction(self.playButton)

        self.pauseButton = QtGui.QAction(self.mainWindow)
        self.pauseButton.triggered.connect(lambda: self.timer.stop())
        iconPause = QtGui.QIcon()
        iconPause.addPixmap(QtGui.QPixmap("images/pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pauseButton.setIcon(iconPause)
        self.toolBar.addAction(self.pauseButton)

        self.fasterButton = QtGui.QAction(self.mainWindow)
        self.fasterButton.triggered.connect(lambda: self.timer.start(50))
        iconFaster = QtGui.QIcon()
        iconFaster.addPixmap(QtGui.QPixmap("images/faster.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.fasterButton.setIcon(iconFaster)
        self.toolBar.addAction(self.fasterButton)
        self.toolBar.addSeparator()

        ### grid
        #grid = gl.GLGridItem()
        #self.view.addItem(grid)

        ### scatter plot
        #self.scatterPlot = gl.GLScatterPlotItem(pxMode=False)
        #self.plantPlot = gl.GLScatterPlotItem(pxMode=False)
        #self.view.addItem(self.scatterPlot)

        ### space
        self.xLimits = -100, 100
        self.yLimits = -100, 100
        self.zLimits = -100, 100

        ### objets
        self.surface = None
        self.water = None

        ### start program
        self.restart()

    def restart(self):
        if self.surface:
            self.view.removeItem(self.surface.mesh)

        if self.water:
            self.view.removeItem(self.water.plot)

        self.surface = Surface(self.xLimits, self.yLimits, self.zLimits)
        self.view.addItem(self.surface.mesh)

        self.water = [Water(self.surface) for i in range(500)]
        for i in range(500):
            self.view.addItem(self.water[i].plot)

    def update(self):
        for i in range(500):
            self.water[i].move()


class Surface():
    def __init__(self, xLimits, yLimits, zLimits):
        self.xMin = np.random.rand() * (xLimits[1]-xLimits[0]) + xLimits[0]
        self.yMin = np.random.rand() * (yLimits[1]-yLimits[0]) + yLimits[0]

        a0 = np.random.rand() * 0.005
        a1 = np.random.rand() * 0.005
        a2 = (np.random.rand() - 0.5) * 0.005
        a3 = -2*a0*self.xMin - a2*self.yMin
        a4 = -2*a1*self.yMin - a2*self.xMin

        self.coef = a0, a1, a2, a3, a4

        side = 21
        x = np.linspace(xLimits[0], xLimits[1], side)
        y = np.linspace(yLimits[0], yLimits[1], side)

        dots = np.zeros((side**2, 3))
        for i in range(side):
            for j in range(side):
                dots[i*side + j] = ([x[i], y[j], self.zpolyn(x[i], y[j])])

        face1 = []
        face2 = []
        for i in range(side-1):
            for j in range(side-1):
                face1.append([side*i+j, side*i+j+1,side*(i+1)+j])
                face2.append([side*(i+1)+j+1, side*i+j+1,side*(i+1)+j])

        faces = np.array(face1 + face2)
        faceColors = np.ones(faces.shape)*0.5
        self.mesh = gl.GLMeshItem(meshdata=gl.MeshData(vertexes=dots, faces=faces, faceColors=faceColors))
        self.mesh.setGLOptions(opts="translucent")

    def zpolyn(self, x, y):
        return self.coef[0]*x**2 + self.coef[1]*y**2 + self.coef[2]*x*y + self.coef[3]*x + self.coef[4]*y

    def gradpolyn(self, x, y):
        v = np.array([2*self.coef[0]*x + self.coef[2]*y + self.coef[3], 2*self.coef[1]*y + self.coef[2]*x + self.coef[4], 1])
        return v/np.dot(v,v)

class Water():
    def __init__(self, Surface):
        self.surface = Surface
        self.state = 'Liquid'
        self.agitation = 10
        self.volume = np.array(5)
        self.color = np.array([0.1, 0.1, 0.9, 0.2])
        self.vel = np.array([0, 0, 0])
        self.pos = np.array([0, 0, 0])
        self.plot = gl.GLScatterPlotItem(pxMode=False)
        self.plot.setData(pos = self.pos, size = self.volume, color = self.color)

    def move(self):
        r = np.random.normal(self.agitation)
        theta = np.random.uniform(0, np.pi)
        vx = r*np.cos(theta)
        vy = r*np.sin(theta)

        grad = self.surface.gradpolyn(self.pos[0], self.pos[1])
        self.vel = self.vel*0.9 + np.dot(grad, np.array([0,0,-10]))*grad
        self.pos = self.pos + self.vel + np.array([vx, vy, 0])

        self.pos[2] = self.surface.zpolyn(self.pos[0], self.pos[1])
        self.plot.setData(pos = self.pos)


def main():
    app = QtGui.QApplication([])
    window = QtGui.QMainWindow()
    window.setWindowTitle('f12')
    window.resize(1000,600)
    window.show()
    ui = Window()
    ui.setupUi(window)
    app.exec_()

if __name__ == "__main__":
    main()

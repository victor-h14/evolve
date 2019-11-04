from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np

class Window(object):    
    def setupUi(self, mainWindow):
        self.mainWindow = mainWindow
        self.mainWindow.setObjectName("Player")
        
        self.view = gl.GLViewWidget()
        self.view.opts['distance'] = 30
        self.mainWindow.setCentralWidget(self.view)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)     
        
        self.toolBar = QtGui.QToolBar(self.mainWindow)
        self.mainWindow.addToolBar(self.toolBar)
        
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
        
        self.dim = 20

        grid = gl.GLGridItem()
        self.view.addItem(grid)

        self.map1 = [["" for j in range(self.dim)] for i in range(self.dim)]
        self.list1 = []
        self.pos = np.zeros((self.dim**2, 3))
        for i in range(self.dim):
            for j in range(self.dim):
                self.pos[i*self.dim + j] = (i -(self.dim-1)/2, j -(self.dim-1)/2, 0)

        self.size = np.ones(self.dim**2)*0.5
        self.color = np.zeros((self.dim**2, 4))
        self.scatterPlot = gl.GLScatterPlotItem(pos=self.pos, size=self.size, color=self.color, pxMode=False)
        self.view.addItem(self.scatterPlot)

        self.map1[0][0] = "A;A"
        self.list1.append(0)
        
    def update(self):
        for i in range(self.dim):
            for j in range(self.dim):
                if(self.map1[i][j] == "A;A"):
                    self.color[i*self.dim + j] = (0, 1, 0, 1)
        self.scatterPlot.setData(color=self.color)
        temp = []
        for index in self.list1:
            j = index % self.dim
            i = (index - j) // self.dim
            r = np.random.randint(4)
            
            if(r==0 and i != self.dim-1):
                if(index + self.dim not in self.list1):
                    temp.append(index + self.dim)
                    self.map1[i+1][j] = "A;A"
                    
            elif(r==1 and i != 0):
                if(index - self.dim not in self.list1):
                    temp.append(index - self.dim)
                    self.map1[i-1][j] = "A;A"
                    
            elif(r==2 and j != self.dim-1):
                if(index + 1 not in self.list1):
                    temp.append(index + 1)
                    self.map1[i][j+1] = "A;A"
                    
            elif(r==3 and j != 0):
                if(index - 1 not in self.list1):
                    temp.append(index - 1)
                    self.map1[i][j-1] = "A;A"
                    
        self.list1 = self.list1 + temp

def main():
    app = QtGui.QApplication([])
    window = QtGui.QMainWindow()
    window.setWindowTitle('f04')
    window.resize(1000,600)
    window.show()
    ui = Window()
    ui.setupUi(window)
    app.exec_()

if __name__ == "__main__":
    main()


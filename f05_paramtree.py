from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import parametertree as pt
import pyqtgraph.opengl as gl
import numpy as np

class Window(object):    
    def setupUi(self, mainWindow):
        self.mainWindow = mainWindow
        self.mainWindow.setObjectName("Player")
        self.dim = 20
        
        ### view
        self.view = gl.GLViewWidget()
        self.view.opts['distance'] = 30
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
        
        self.plant = Plant(self.dim)
        self.plant.xCoord.sigValueChanged.connect(self.track)
        self.plant.yCoord.sigValueChanged.connect(self.track)
        self.parameterTree.addParameters(self.plant)
        
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
        
        self.analyzeButton = QtGui.QAction(self.mainWindow)
        self.analyzeButton.triggered.connect(self.track)
        iconAnalyze = QtGui.QIcon()
        iconAnalyze.addPixmap(QtGui.QPixmap("images/analyze.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.analyzeButton.setIcon(iconAnalyze)
        self.toolBar.addAction(self.analyzeButton)
        
        ### algorithm
        grid = gl.GLGridItem()
        self.view.addItem(grid)
        self.scatterPlot = gl.GLScatterPlotItem(pxMode=False)
        self.view.addItem(self.scatterPlot)
        self.restart()
        
    
    def restart(self):
        self.map1 = [[";" for j in range(self.dim)] for i in range(self.dim)]
        self.list1 = []
        self.pos = np.zeros((self.dim**2, 3))
        for i in range(self.dim):
            for j in range(self.dim):
                self.pos[i*self.dim + j] = (i -(self.dim-1)/2, j -(self.dim-1)/2, 0)
        
        self.size = np.ones(self.dim**2)*0.5
        self.color = np.zeros((self.dim**2, 4))
        self.scatterPlot.setData(pos=self.pos, size=self.size, color=self.color)

        self.map1[0][0] = "A;A"
        self.list1.append(0)
    
    def update(self):
        self.dockParameterTree.setVisible(False)
        for i in range(self.dim):
            for j in range(self.dim):
                if(self.map1[i][j] != ';'):
                    r, g, b, a = 0, 1, 0, 1
                    for gene in self.map1[i][j]:
                        if(gene == 'A'):
                            g -= 0.1
                        elif(gene == 'B'):
                            r += 0.3
                    self.color[i*self.dim + j] = (r, g, b, a)
        self.scatterPlot.setData(color=self.color)
        temp = []
        for index in self.list1:
            j = index % self.dim
            i = (index - j) // self.dim
            r = np.random.randint(4)
            genotype = self.map1[i][j] 
            for chromosome in genotype.split(';'):
                if(chromosome == ''):
                    r = 5 
            
            if(r==0 and i != self.dim-1):
                if(index + self.dim not in self.list1):
                    temp.append(index + self.dim)
                    self.map1[i+1][j] = self.meiosis(genotype) + ";" + self.meiosis(genotype)
                    
            elif(r==1 and i != 0):
                if(index - self.dim not in self.list1):
                    temp.append(index - self.dim)
                    self.map1[i-1][j] = self.meiosis(genotype) + ";" + self.meiosis(genotype)
                    
            elif(r==2 and j != self.dim-1):
                if(index + 1 not in self.list1):
                    temp.append(index + 1)
                    self.map1[i][j+1] = self.meiosis(genotype) + ";" + self.meiosis(genotype)
                    
            elif(r==3 and j != 0):
                if(index - 1 not in self.list1):
                    temp.append(index - 1)
                    self.map1[i][j-1] = self.meiosis(genotype) + ";" + self.meiosis(genotype)
                    
        self.list1 = self.list1 + temp

    def track(self):
        self.timer.stop()
        self.dockParameterTree.setVisible(True)
        x = self.plant.xCoord.value()
        y = self.plant.yCoord.value()
        genotype = self.map1[x][y]
        self.plant.genotype.setValue(self.map1[x][y])
        self.plant.color.setValue(str(self.color[x*self.dim+y]))
        color = np.zeros((self.dim**2, 4))
        if(genotype):
            color[x*self.dim+y] = self.color[x*self.dim+y]
        self.scatterPlot.setData(color=color)

    def meiosis(self, genotype):
        chromosome = genotype.split(';')
        error = 0.01
        duplGene, duplChr, deleGene, chanGene, r = np.random.rand(5)
        
        i = r > 0.5
        n = len(chromosome[i])
        
        if(duplGene < error):
            r = np.random.randint(n)
            chromosome[i] = chromosome[i][:r] + chromosome[i][r] + chromosome[i][r:]
        if(duplChr < error):
            chromosome[i] = chromosome[i]*2
        if(deleGene < error):
            r = np.random.randint(n)
            chromosome[i] = chromosome[i][:r] + chromosome[i][r+1:]
        if(chanGene < error):
            genes = ['A', 'B']
            s = np.random.randint(len(genes))
            r = np.random.randint(n)
            chromosome[i] = chromosome[i][:r] + genes[s] + chromosome[i][r+1:]
        
        return chromosome[i]

class Plant(pt.parameterTypes.GroupParameter):
    def __init__(self, dim, **opts):
        opts['name'] = 'Plant'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        self.xCoord = self.addChild({'name': 'x', 'type': 'int', 'value': 0, 'limits': (0, dim-1)})
        self.yCoord = self.addChild({'name': 'y', 'type': 'int', 'value': 0, 'limits': (0, dim-1)})
        self.species = self.addChild({'name': 'Species', 'type': 'str', 'value': 'Species 1', 'readonly': True})
        self.genotype = self.addChild({'name': 'Genotype', 'type': 'str', 'value': '', 'readonly': True})
        self.color = self.addChild({'name': 'Color RGBalpha', 'type': 'str', 'value': '(0, 0, 0, 0)', 'readonly': True})

def main():
    app = QtGui.QApplication([])
    window = QtGui.QMainWindow()
    window.setWindowTitle('f05')
    window.resize(1000,600)
    window.show()
    ui = Window()
    ui.setupUi(window)
    app.exec_()

if __name__ == "__main__":
    main()


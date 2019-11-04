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
        self.pos = np.zeros((self.dim**2, 3))
        for i in range(self.dim):
            for j in range(self.dim):
                self.pos[i*self.dim + j] = (i -(self.dim-1)/2, j -(self.dim-1)/2, 0)
        
        self.size = np.ones(self.dim**2)*0.5
        self.color = np.zeros((self.dim**2, 4))
        self.scatterPlot.setData(pos=self.pos, size=self.size, color=self.color)

        mid = self.dim // 2
        self.map1[mid][mid] = 'A;A'
        self.dict1 = {mid*(self.dim+1): 1}
    
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
        temp = {}
        for index in self.dict1.keys():
            j = index % self.dim
            i = (index - j) // self.dim
            
            genotypeA = self.map1[i][j] 
            gameteA = self.meiosis(genotypeA)
            
            min_row = max(i-1, 0)
            max_row = min(i+1, self.dim-1)
            min_col = max(j-1, 0)
            max_col = min(j+1, self.dim-1)
            genotypeNew = ''
            
            for row in range(min_row, max_row):
                for col in range(min_col, max_col):
                    genotypeB = self.map1[row][col]
                    if(genotypeB != ';'):
                        gameteB = self.meiosis(genotypeB)
                        if(gameteA or gameteB):
                            genotypeNew = gameteA + ';' + gameteB
                            break
            
            if(genotypeNew):
                rowNew = np.random.randint(min_row, max_row + 1)
                colNew = np.random.randint(min_col, max_col + 1)
                if(rowNew*self.dim + colNew not in self.dict1):
                    temp[rowNew*self.dim + colNew] = 1
                    self.map1[rowNew][colNew] = genotypeNew
            
        self.dict1.update(temp)

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
        genes = ['A', 'B']
        error = 0.02
        duplGene, duplChr, deleGene, chanGene, r = np.random.rand(5)
        
        i = r > 0.5
        n = len(chromosome[i])
        
        if(n == 0):
            if(chanGene < error):
                s = np.random.randint(len(genes))
                return genes[s]
            return ''
                    
        if(duplGene < error):
            r = np.random.randint(n)
            chromosome[i] = chromosome[i][:r] + chromosome[i][r] + chromosome[i][r:]
        if(duplChr < error):
            chromosome[i] = chromosome[i]*2
        if(deleGene < error):
            r = np.random.randint(n)
            chromosome[i] = chromosome[i][:r] + chromosome[i][r+1:]
        if(chanGene < error):
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
    window.setWindowTitle('f06')
    window.resize(1000,600)
    window.show()
    ui = Window()
    ui.setupUi(window)
    app.exec_()

if __name__ == "__main__":
    main()


from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import parametertree as pt
import random
import pyqtgraph.opengl as gl
import numpy as np

class Window(object):    
    def setupUi(self, mainWindow):
        self.mainWindow = mainWindow
        self.mainWindow.setObjectName("Player")
        self.l = 20
        
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
        
        self.plant = Plant(self.l)
        self.plant.index.sigValueChanged.connect(self.track)
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
        
        ### grid
        grid = gl.GLGridItem()
        self.view.addItem(grid)
        
        ### scatter plot
        self.scatterPlot = gl.GLScatterPlotItem(pxMode=False)
        self.view.addItem(self.scatterPlot)
        
        ### start program
        self.restart()
        
        
    def restart(self):                  #goes back to one plant at the origin
        self.plants = ['.A1.C1.;.A1.C1.']
        self.geneColor = {'A1': (0,1,0,1)}
        self.geneSpread = {'C1': 1}
        self.pos = np.zeros((1, 3))
        self.size = np.ones(1)*0.5
        self.colors = np.array([[0, 1, 0, 1]])
        self.scatterPlot.setData(pos=self.pos, size=self.size, color=self.colors)
        
        
    def update(self):                   #each time step
        self.dockParameterTree.setVisible(False)            
        self.scatterPlot.setData(pos=self.pos, size=self.size, color=self.colors)
        print(len(self.plants), "individuals")
        
        #adding new plants  
        self.temp = []
        for i in range(len(self.plants)):
            j = np.random.randint(len(self.plants))
            gameteA = self.meiosis(self.plants[i]) #female plant
            gameteB = self.meiosis(self.plants[j]) #male plant
            newGenotype = gameteA + ';' + gameteB
            
            controlColor = False
            controlSpread = False
            for gene in newGenotype.split('.'): 
                if(gene in self.geneColor):
                    controlColor = True
                if(gene in self.geneSpread):
                    controlSpread = True

            if(controlSpread and controlColor):
                c = self.spread(self.plants[i])
                r = random.gauss(0, c)
                theta = random.uniform(0, 2*np.pi)
                x0, y0, z0 = self.pos[i] 
                x = x0 + r*np.cos(theta)
                y = y0 + r*np.sin(theta)
                
                if(x >= -self.l/2 and x <= self.l/2):
                    if(y >= -self.l/2 and y <= self.l/2):
                        self.birth(newGenotype, x, y)

        self.plants += self.temp
        
        
    def track(self):                    #look at each plant individually
        self.timer.stop()
        self.dockParameterTree.setVisible(True)
        
        i = self.plant.index.value()
        pos = self.pos[i]
        self.plant.index.setLimits((0, len(self.plants)))
        self.plant.xCoord.setValue(pos[0])
        self.plant.yCoord.setValue(pos[1])
        self.plant.zCoord.setValue(pos[2])
        self.plant.genotype.setValue(self.plants[i])
        self.plant.color.setValue(str(self.colors[i]))
        colors = np.copy(self.colors)
        colors[i] = [1, 1, 1, 1]
        self.scatterPlot.setData(color=colors)
        
        
    def z(self, x, y):                  #function that describes the surface height
        return 0
    
        
    def birth(self, genotype, x, y):    #function that set the rules for a new plant to come
        def probabilityFunction(d):     #probability of birth given the minimun distance
            return 2*d**2/(1 + d**4) 
    
        coords = x, y, self.z(x, y)
        distance = min([sum([(pos[i] - coords[i])**2 for i in range(2)]) for pos in self.pos])
        r = np.random.rand()
        if(probabilityFunction(distance) > r):
            self.pos = np.append(self.pos, [coords], axis = 0)
            self.colors = np.append(self.colors, [self.color(genotype)], axis = 0)
            self.size = np.append(self.size, 0.5)
            self.temp.append(genotype)
    
    
    def color(self, genotype):          #function that describes the color of a plant
        n = 0
        r, g, b, a = 0, 0, 0, 0
        for gene in genotype.split('.'):
            if(gene in self.geneColor):
                color = self.geneColor[gene]
                r += color[0]
                g += color[1]
                b += color[2]
                a += color[3]
                n += 1
        return r/n, g/n, b/n, a/n
        
    def spread(self, genotype):         #function that describes the spread of a plant offspring
        n = 0
        c = 0
        for gene in genotype.split('.'):
            if(gene in self.geneSpread):
                c += self.geneSpread[gene]
                n += 1
        return c/n
        
        
    def meiosis(self, genotype):        #rules to form new gamets
        r = np.random.rand()
        if(r > 0.5):
            chromosome = genotype[0 : genotype.index(';')]
        else:
            chromosome = genotype[genotype.index(';') + 1 : ]
        
        error = 0.01
        newChromosome = []
        
        for gene in chromosome.split('.'):
            if(gene == ''):
                pass
            duplGene, deleGene, mutaGene = np.random.rand(3) 
            if(mutaGene < error):       #create a new allele for the gene
                if(gene in self.geneColor):
                    number = str(len(self.geneColor) + 1)
                    value = list(np.random.rand(3)) + [1]
                    self.geneColor.update({'A' + number:value})
                    newChromosome += ['A' + number] 
                elif(gene in self.geneSpread):
                    number = str(len(self.geneSpread) + 1)
                    value = self.geneSpread[gene] + random.gauss(0, 1)
                    self.geneSpread.update({'C' + number:value})
                    newChromosome += ['C' + number]
            
            elif(duplGene < error):     #duplicate the gene
                newChromosome += [gene]
                
            elif(deleGene > error):     #delete the gene
                newChromosome += [gene]
        
        duplChr = np.random.rand()
        if(duplChr < error):
            newChromosome += newChromosome
        
        strChromosome = '.'
        for gene in newChromosome:
            if(gene != ''):
                strChromosome += gene + '.'
        
        return strChromosome

######################################## ParameterTree item ########################################

class Plant(pt.parameterTypes.GroupParameter):
    def __init__(self, size, **opts):
        opts['name'] = 'Plant'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        self.index = self.addChild({'name': 'Index', 'type': 'int', 'value': 0})
        self.xCoord = self.addChild({'name': 'x', 'type': 'float', 'value': 0, 'readonly': True})
        self.yCoord = self.addChild({'name': 'y', 'type': 'float', 'value': 0, 'readonly': True})
        self.zCoord = self.addChild({'name': 'z', 'type': 'float', 'value': 0, 'readonly': True})
        self.species = self.addChild({'name': 'Species', 'type': 'str', 'value': 'Species 1', 'readonly': True})
        self.genotype = self.addChild({'name': 'Genotype', 'type': 'str', 'value': '', 'readonly': True})
        self.color = self.addChild({'name': 'Color RGBalpha', 'type': 'str', 'value': '(0, 0, 0, 0)', 'readonly': True})


def main():
    app = QtGui.QApplication([])
    window = QtGui.QMainWindow()
    window.setWindowTitle('f08')
    window.resize(1000,600)
    window.show()
    ui = Window()
    ui.setupUi(window)
    app.exec_()

if __name__ == "__main__":
    main()


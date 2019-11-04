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
        grid = gl.GLGridItem()
        self.view.addItem(grid)
        
        ### scatter plot
        self.scatterPlot = gl.GLScatterPlotItem(pxMode=False)
        self.plantPlot = gl.GLScatterPlotItem(pxMode=False)
        self.view.addItem(self.scatterPlot)

        ### setting an animal
        self.animal = Animal()
        self.plantNumber = 50
        #self.plant.index.sigValueChanged.connect(self.track)
        self.parameterTree.addParameters(self.animal)
        self.view.addItem(self.plantPlot)

        ### start program
        self.restart()
        self.a = 0
        
        
    def restart(self):
        self.pos = np.zeros((1, 3))
        self.colors = np.array([self.animal.color])
        self.size = [self.animal.size.value() * 0.1]
        self.scatterPlot.setData(pos=self.pos, size=self.size, color=self.colors)
        
        self.plantPos = np.random.rand(self.plantNumber, 3) * np.array([20, 20, 0]) - np.array([10, 10, 0])
        plantColor = np.ones((self.plantNumber, 4)) * np.array([0, 1, 0, 0.5])
        plantSize = np.ones(self.plantNumber) * 0.5
        self.plantPlot.setData(pos=self.plantPos, size=plantSize, color=plantColor)
        
        
    def update(self):
        self.animal.update_countdowns()
        self.colors = np.array([self.animal.color])
        self.size = [self.animal.size.value() * 0.1]
        self.pos = self.pos + (np.random.rand(1, 3) - np.ones(shape=(1,3)) * 0.5) * np.array([1, 1, 0])
        if self.pos[0][0] > 10:
            self.pos[0][0] = 10
        elif self.pos[0][0] < -10:
            self.pos[0][0] = -10
        
        if self.pos[0][1] > 10:
            self.pos[0][1] = 10
        elif self.pos[0][1] < -10:
            self.pos[0][1] = -10
        
        self.scatterPlot.setData(pos=self.pos, size=self.size, color=self.colors)
        self.plant()
        self.eat()
        
        #if self.animal.life.value() <= 0:
        #    self.timer.stop()
        
    def plant(self):
        temp = np.random.rand(1, 3) * np.array([20, 20, 0]) - np.array([10, 10, 0])
        for i in range(len(self.plantPos) - 1):
            self.plantPos[i] = self.plantPos[i+1]
        self.plantPos[-1] = temp
        self.plantPlot.setData(pos=self.plantPos)
    
    def eat(self):
        def distance(coord1, coord2):
            return sum([(coord1[i] - coord2[i])**2 for i in range(3)])**0.5
        
        for i in range(len(self.plantPos)):
            if (distance(self.plantPos[i], self.pos[0]) < self.size[0]):
                self.animal.food_eaten('plant', 1)
                self.plantPos[i] = [0, 0, 100]
        
class Animal(pt.parameterTypes.GroupParameter):
    def __init__(self, **opts):
        opts['name'] = 'Animal'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        self.index = self.addChild({'name': 'Index', 'type': 'int', 'value': 0})
        self.life = self.addChild({'name': 'Life', 'type': 'float', 'value': 100, 'readonly': True})
        self.strength = self.addChild({'name': 'Strength', 'type': 'int', 'value': 0, 'readonly': True})
        self.sociability = self.addChild({'name': 'Sociability', 'type': 'int', 'value': 0, 'readonly': True})
        self.size = self.addChild({'name': 'Size', 'type': 'int', 'value': 1, 'readonly': True})
        self.speed = self.addChild({'name': 'Speed', 'type': 'int', 'value': 0, 'readonly': True})
        self.plantEater = self.addChild({'name': 'Plant Eater', 'type': 'int', 'value': 0, 'readonly': True})
        self.meatEater = self.addChild({'name': 'Meat Eater', 'type': 'int', 'value': 0, 'readonly': True})
        self.color = [0.5, 0.5, 0.5, 1]
        
        #genetic structure
        self.genes = ['mainregulator', 'grow0', 'reproduce0']
        self.relations = {'mainregulator': [['grow0', 10], ['reproduce0', 100]]}
        self.countdowns = {}
        self.timespans = {}
        
        self.set_timespans()
        
    def set_timespans(self):
        #all genes begin with timespans = 0 except the main regulator
        for gene in self.genes:
            self.timespans[gene] = 0
        self.timespans['mainregulator'] = 1
        
        for regulator in self.relations:
            for relation in self.relations[regulator]:
                if 'regulator' in relation[0]:
                    self.timespans[relation[0]] += self.timespans[regulator] * relation[1]
        
        for regulator in self.relations:
            for relation in self.relations[regulator]:
                if 'regulator' not in relation[0]:
                    self.timespans[relation[0]] += self.timespans[regulator] * relation[1]
        
        self.countdowns = self.timespans.copy()
        
    def update_countdowns(self):
        self.life.setValue(self.life.value() - 0.1 * self.size.value())

        for gene in self.countdowns:
            if self.countdowns[gene] > 0:
                self.countdowns[gene] -= 1
            elif self.countdowns[gene] == 0:
                self.gene_effect(gene)
                self.countdowns[gene] = self.timespans[gene]
        
    def gene_effect(self, gene):
        if 'grow' in gene:
            self.size.setValue(self.size.value() + 1)
            self.strength.setValue(self.strength.value() + 1)
            self.speed.setValue(self.speed.value() - 1)
        elif 'reproduce' in gene:
            self.life.setValue(self.life.value() * 0.5)
            #must do
        elif 'red+' in gene:
            self.color[0] += (1 - self.color[0])/2
        elif 'red-' in gene:
            self.color[0] -= self.color[0]/2 
        elif 'green+' in gene:
            self.color[1] += (1 - self.color[1])/2
        elif 'green-' in gene:
            self.color[1] -= self.color[1]/2
        elif 'blue+' in gene:
            self.color[2] += (1 - self.color[2])/2
        elif 'blue-' in gene:
            self.color[2] -= self.color[2]/2
        elif 'stronger' in gene:
            self.strength.setValue(self.strength.value() + 1)
        elif 'faster' in gene:
            self.speed.setValue(self.speed.value() + 1)
        elif 'veggie' in gene:
            self.plantEater.setValue(self.plantEater.value() + 2)
            self.meatEater.setValue(self.plantEater.value() - 1)
            self.speed.setValue(self.speed.value() + 1)
        elif 'meat' in gene:
            self.meatEater.setValue(self.meatEater.value() + 2)
            self.plantEater.setValue(self.plantEater.value() - 1)
            self.strength.setValue(self.strength.value() + 1)
        elif 'sociable' in gene:
            self.sociability.setValue(self.sociability.value() + 1)
        elif 'die' in gene:
            self.life.setValue(0)
        elif 'something' in gene:
            pass
            #must do
    
    def food_eaten(self, food, size):
        x1 = self.plantEater.value()
        x2 = self.meatEater.value()
        foodFactor = 1
        if x1 != x2:
            foodFactor = 2**((x1 - x2)/(abs(x1) + abs(x2)))
        
        if food == 'plant':
            self.life.setValue(self.life.value() + 10 * foodFactor)
        elif food == 'animal':
            self.life.setValue(self.life.value() + 10 * size / foodFactor)

def main():
    app = QtGui.QApplication([])
    window = QtGui.QMainWindow()
    window.setWindowTitle('f09')
    window.resize(1000,600)
    window.show()
    ui = Window()
    ui.setupUi(window)
    app.exec_()

if __name__ == "__main__":
    main()


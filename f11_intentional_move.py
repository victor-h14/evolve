#nao funfa

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
        #grid = gl.GLGridItem()
        #self.view.addItem(grid)
        
        ### scatter plot
        self.scatterPlot = gl.GLScatterPlotItem(pxMode=False)
        self.plantPlot = gl.GLScatterPlotItem(pxMode=False)
        self.view.addItem(self.scatterPlot)

        ### setting an animal
        self.animals = []
        self.plantNumber = 100
        self.distanceAnimals = [[]]
        self.distancePlants = [[]]
        #self.plant.index.sigValueChanged.connect(self.track)
        #self.parameterTree.addParameters(self.animal)
        self.view.addItem(self.plantPlot)

        ### start program
        self.restart()

    def restart(self):
        #restarting animals
        self.animals = [Animal()]
        self.pos = np.zeros((1, 3))
        self.color = np.array([self.animals[0].color])
        self.size = [self.animals[0].size.value() * 0.1]
        self.scatterPlot.setData(pos=self.pos, size=self.size, color=self.color)
        
        #restarting plants
        self.plantPos = np.random.rand(self.plantNumber, 3) * np.array([20, 20, 0]) - np.array([10, 10, 0])
        plantColor = np.ones((self.plantNumber, 4)) * np.array([0, 1, 0, 0.5])
        plantSize = np.ones(self.plantNumber) * 0.5
        self.plantPlot.setData(pos=self.plantPos, size=plantSize, color=plantColor)
        
        
    def update(self):
        for i in range(len(self.animals)):
            self.animals[i].update_countdowns()
            self.color[i] = self.animals[i].color
            self.size[i] = self.animals[i].size.value() * 0.1
            self.move(i)
        
        self.update_distances()
        self.scatterPlot.setData(pos=self.pos, size=self.size, color=self.color)
        self.plant()
        self.eat()
        self.born()
        self.die()
    
    def update_distances(self):
        def distance(coord1, coord2):
            return sum([(coord1[i] - coord2[i])**2 for i in range(3)])**0.5
        
        self.distancePlants = []
        for i in range(len(self.animals)):
            temp = []
            for j in range(len(self.plantPos)):
                temp += [distance(self.plantPos[j], self.pos[i])]
            self.distancePlants.append(temp)
        
        self.distanceAnimals = []
        for i in range(len(self.animals)):
            temp = []
            for j in range(len(self.animals)):
                temp += [distance(self.pos[j], self.pos[i])]
            self.distanceAnimals.append(temp)
        
    def plant(self):
        temp = np.random.rand(1, 3) * np.array([20, 20, 0]) - np.array([10, 10, 0])
        for i in range(len(self.plantPos) - 1):
            self.plantPos[i] = self.plantPos[i+1]
        self.plantPos[-1] = temp
        self.plantPlot.setData(pos=self.plantPos)
    
    def move(self, i):
        #random contribution
        randomMove = (np.random.rand(1, 3) - np.ones(shape=(1,3)) * 0.5) * np.array([1, 1, 0])
        
        #total = running + sociability + hunting
        
        #runner contribution
        running = self.animals[i].running.value()
        if running > 0:
            distance = 100
            index = i
            for j in self.distanceAnimals[i]:
                if self.distanceAnimals[i][j] < distance and self.distanceAnimals[i][j] > 0:
                    distance = self.distanceAnimals[i][j]
                    index = j
            
            runningMove = np.array([self.pos[i][k] - self.pos[index][k] for k in range(3)])/distance            
        else:
            runningMove = 0
        
        #sociable contribution
        #sociability = self.animals[i].sociability.value()
        
        #hunter contribution
        #hunting = self.animals[i].hunting.value()

        move = (randomMove + running * runningMove)/(1 + running) * self.animals[i].speed.value() * 0.1
        self.pos[i] = self.pos[i] + move

        if self.pos[i][0] > 10:
            self.pos[i][0] = 10
        elif self.pos[i][0] < -10:
            self.pos[i][0] = -10
        
        if self.pos[i][1] > 10:
            self.pos[i][1] = 10
        elif self.pos[i][1] < -10:
            self.pos[i][1] = -10

    def eat(self):
        for i in range(len(self.animals)):
            for j in range(len(self.plantPos)):
                if self.distancePlants[i][j] < 1 + 0.1 * self.size[i]:
                    self.animals[i].food_eaten('plant', 5)
                    self.plantPos[j] = [0, 0, 100]
                    self.update_distances()
                    
    
    def born(self):
        for i in range(len(self.animals)):
            if self.animals[i].breed != None:
                animal = self.animals[i].breed
                self.animals[i].breed = None
                self.animals += [animal]
                n = len(self.animals)
                self.pos = np.resize(self.pos, (n, 3))
                self.pos[-1] = self.pos[i]
                self.color = np.resize(self.color, (n, 4))
                self.color[-1] = animal.color
                self.size = np.resize(self.size, (n))
                self.size[-1] = animal.size.value()
    
    def die(self):
        dead = []
        n = len(self.animals)
        for i in range(n):
            if self.animals[i].life.value() <= 0:
                dead += [i]
        m = len(dead)
        if m != 0:
            for i in dead[::-1]:
                del self.animals[i]
            pos = np.zeros((n-m, 3))
            color = np.zeros((n-m, 4))
            size = np.zeros((n-m))
            j = 0
            for i in range(n):
                if i not in dead:
                    pos[j] = self.pos[i]
                    color[j] = self.color[i]
                    size[j] = self.size[i]
                    j+=1
            self.pos = pos
            self.color = color
            self.size = size
            
class Animal(pt.parameterTypes.GroupParameter):
    def __init__(self, genes = None, relations = None, **opts):
        opts['name'] = 'Animal'
        opts['type'] = 'bool'
        opts['value'] = True
        pt.parameterTypes.GroupParameter.__init__(self, **opts)

        self.index = self.addChild({'name': 'Index', 'type': 'int', 'value': 0})
        self.life = self.addChild({'name': 'Life', 'type': 'float', 'value': 100, 'readonly': True})
        self.strength = self.addChild({'name': 'Strength', 'type': 'int', 'value': 0, 'readonly': True})
        self.sociability = self.addChild({'name': 'Sociability', 'type': 'int', 'value': 0, 'readonly': True})
        self.running = self.addChild({'name': 'Running', 'type': 'int', 'value': 0, 'readonly': True})
        self.hunting = self.addChild({'name': 'Hunting', 'type': 'int', 'value': 0, 'readonly': True})
        self.size = self.addChild({'name': 'Size', 'type': 'int', 'value': 1, 'readonly': True})
        self.speed = self.addChild({'name': 'Speed', 'type': 'int', 'value': 10, 'readonly': True})
        self.plantEater = self.addChild({'name': 'Plant Eater', 'type': 'int', 'value': 0, 'readonly': True})
        self.meatEater = self.addChild({'name': 'Meat Eater', 'type': 'int', 'value': 0, 'readonly': True})
        self.color = [0.5, 0.5, 0.5, 1]
        self.breed = None
        
        #gene classes
        self.geneClasses = ['grow', 'reproduce', 'red+', 'red-', 'green+',
                            'green-', 'blue+', 'blue-', 'stronger', 'faster',
                            'veggie', 'meat', 'sociable', 'runner', 'hunter', 'die']
        
        #genetic structure
        if genes == None:
            self.genes = ['mainregulator', 'grow0', 'reproduce0']
        else:
            self.genes = genes
        
        if relations == None:
            self.relations = {'mainregulator': [['grow0', 10], ['reproduce0', 50]]}
        else:
            self.relations = relations
        self.countdowns = {}
        self.timespans = {}
        self.set_timespans()
        
    def set_timespans(self):
        #all genes begin with timespans = 0 except the main regulator
        for gene in self.genes:
            self.timespans[gene] = 0
        for relation in self.relations.values():
            for r in relation:
                self.timespans[r[0]] = 0
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
        self.life_update()
        for gene in self.countdowns:
            if self.countdowns[gene] > 0:
                self.countdowns[gene] -= 1
            elif self.countdowns[gene] == 0:
                self.gene_effect(gene)
                self.countdowns[gene] = self.timespans[gene]
    
    def life_update(self):
        animalSize = self.size.value()
        genomeSize = len(self.genes)
        self.life.setValue(self.life.value() - 0.2 * animalSize - 0.2 * genomeSize)
        
    def gene_effect(self, gene):
        if 'grow' in gene:
            self.size.setValue(self.size.value() + 1)
            self.strength.setValue(self.strength.value() + 1)
            self.speed.setValue(self.speed.value() - 1)
        elif 'reproduce' in gene:
            if self.life.value() >= 50:
                self.life.setValue(self.life.value() * 0.5)
                self.reproduce()
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
        elif 'runner' in gene:
            self.running.setValue(self.running.value() + 1)
        elif 'hunter' in gene:
            self.hunting.setValue(self.hunting.value() + 1)
        elif 'die' in gene:
            self.life.setValue(0)

    def prey_traits(self):
        size = self.size.value()
        color = [0, 0, 0]
        
        for gene in self.genes:
            if 'huntBig' in gene:
                size += 1
            elif 'huntSmall' in gene:
                size -= 1
            elif 'huntR+' in gene:
                color[0] += 1
            elif 'huntR-' in gene:
                color[0] -= 1
            elif 'huntG+' in gene:
                color[1] += 1
            elif 'huntG-' in gene:
                color[1] -= 1
            elif 'huntB+' in gene:
                color[2] += 1
            elif 'huntB-' in gene:
                color[2] -= 1
        
        for i in range(3):
            if color[i] == 0:
                color[i] == 0.5
            else:
                color[i] = 0.5 + 0.5 * color[i]/abs(color[i])
        
        return size, color
        
    def reproduce(self):
        self.breed = Animal(self.genes.copy(), self.relations.copy())
        
        #adding a new gene to the gene set
        if np.random.rand() < 0.1:
            newGene = self.geneClasses[np.random.randint(len(self.geneClasses))]
            newIndex = 0
            for gene in self.breed.genes:
                if newGene in gene:
                    newIndex += 1
            self.breed.genes.append(newGene + str(newIndex))
        
        #adding a new regulator
        if np.random.rand() < 0.2:
            newIndex = -1
            for gene in self.breed.genes:
                if 'regulator' in gene:
                    newIndex += 1
            self.breed.genes.append('regulator' + str(newIndex))
        
        #adding new regulation
        for gene in self.breed.genes:
            if 'regulator' in gene and np.random.rand() < 0.1:
                if gene not in self.breed.relations:
                    self.breed.relations[gene] = []
                intensity = np.random.randint(-100, 101)
                regulated = self.breed.genes[np.random.randint(1, len(self.breed.genes))]
                while regulated == gene:
                    regulated = self.breed.genes[np.random.randint(1, len(self.breed.genes))]
                self.breed.relations[gene].append([regulated, intensity])
        print(self.breed.relations)       
    
    def food_eaten(self, food, size):
        x1 = self.plantEater.value()
        x2 = self.meatEater.value()
        foodFactor = 1
        if x1 != x2:
            foodFactor = 2**((x1 - x2)/(abs(x1) + abs(x2)))
        
        if food == 'plant':
            self.life.setValue(self.life.value() + 10 * size * foodFactor)
        elif food == 'animal':
            self.life.setValue(self.life.value() + 10 * size / foodFactor)

def main():
    app = QtGui.QApplication([])
    window = QtGui.QMainWindow()
    window.setWindowTitle('f10')
    window.resize(1000,600)
    window.show()
    ui = Window()
    ui.setupUi(window)
    app.exec_()

if __name__ == "__main__":
    main()

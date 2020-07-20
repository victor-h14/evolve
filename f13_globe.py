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

        self.dryButton = QtGui.QAction(self.mainWindow)
        self.dryButton.triggered.connect(self.draw_dryness)
        iconDry = QtGui.QIcon()
        iconDry.addPixmap(QtGui.QPixmap("images/fire.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.dryButton.setIcon(iconDry)
        self.toolBar.addAction(self.dryButton)

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

        ### scatter plot
        self.plantPlot = gl.GLScatterPlotItem(pxMode=False)
        self.plantPlot.setGLOptions(opts="opaque")
        self.view.addItem(self.plantPlot)

        ### dimensionstranslucent
        self.landradious = 10
        self.waterradious = 10.5

        ### objets
        self.land = None
        self.water = None
        self.dryActive = False
        self.plants = []
        self.plantPosCart = None
        self.plantPosEsf = None
        self.plantSize = None
        self.plantColor = None
        self.geneColor = {}
        self.geneSpread = {}

        ### start program
        self.restart()

    def restart(self):
        if self.land:
            self.view.removeItem(self.land.mesh)

        self.land = Surface(4, self.landradious, np.array((0.5, 0.5, 0.5)))
        self.view.addItem(self.land.mesh)

        self.water = Surface(0, self.waterradious, np.array((0.1, 0.1, 0.9)))
        self.view.addItem(self.water.mesh)

        self.globe = Globe(self.land, self.water)

        self.plants = ['.A1.C1.;.A1.C1.']
        self.geneColor = {'A1': (0,1,0,1)}
        self.geneSpread = {'C1': 1}

        theta, phi = np.pi, np.pi/2
        while(self.globe.height(theta, phi) < 0):
            theta = np.random.beta(1,1)*np.pi*2
            phi = np.random.beta(2,2)*np.pi
        r = self.globe.r(theta, phi)+0.1
        self.plantPosEsf = np.array([[r, theta, phi]])
        self.plantPosCart = np.array([self.land.cart(r, theta, phi)])

        self.plantSize = np.ones(1)*0.5
        self.plantColor = np.array([[0, 1, 0, 1]])
        self.plantPlot.setData(pos=self.plantPosCart, size=self.plantSize, color=self.plantColor)


    def update(self):
        self.dockParameterTree.setVisible(False)
        self.plantPlot.setData(pos=self.plantPosCart, size=self.plantSize, color=self.plantColor)
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
                spr = self.spread(self.plants[i])
                rand = (np.random.beta(1, 1, 2)-0.5)*spr
                pos = self.plantPosEsf[i]
                theta = pos[1] + rand[0]
                phi = pos[2] + rand[1]

                theta = theta % 2*np.pi
                phi = phi % np.pi
                self.birth(newGenotype, theta, phi)

        self.plants += self.temp

    """
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
    """

    def birth(self, genotype, theta, phi):
        def probabilityFunction(d):
            return 2*d**2/(1 + d**4)

        coords = self.land.cart(self.globe.r(theta, phi)+0.1, theta, phi)
        distance = min([sum([(pos[i] - coords[i])**2 for i in range(2)]) for pos in self.plantPosCart])
        r = np.random.rand()
        if(probabilityFunction(distance) > r):
            self.plantPosCart = np.append(self.plantPosCart, [coords], axis = 0)
            self.plantPosEsf = np.append(self.plantPosEsf, [[self.globe.r(theta, phi)+0.1, theta, phi]], axis = 0)
            self.plantColor = np.append(self.plantColor, [self.color(genotype)], axis = 0)
            self.plantSize = np.append(self.plantSize, 0.5)
            self.temp.append(genotype)

    def color(self, genotype):
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

    def spread(self, genotype):
        n = 0
        c = 0
        for gene in genotype.split('.'):
            if(gene in self.geneSpread):
                c += self.geneSpread[gene]
                n += 1
        return c/n

    def meiosis(self, genotype):
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
            if(mutaGene < error):
                if(gene in self.geneColor):
                    number = str(len(self.geneColor) + 1)
                    value = list(np.random.rand(3)) + [1]
                    self.geneColor.update({'A' + number:value})
                    newChromosome += ['A' + number]
                elif(gene in self.geneSpread):
                    number = str(len(self.geneSpread) + 1)
                    value = self.geneSpread[gene] + np.random.normal(0, 1)
                    self.geneSpread.update({'C' + number:value})
                    newChromosome += ['C' + number]

            elif(duplGene < error):
                newChromosome += [gene]

            elif(deleGene > error):
                newChromosome += [gene]

        duplChr = np.random.rand()
        if(duplChr < error):
            newChromosome += newChromosome

        strChromosome = '.'
        for gene in newChromosome:
            if(gene != ''):
                strChromosome += gene + '.'

        return strChromosome

    def draw_dryness(self):
        if(self.dryActive):
            self.dryActive = False
            self.view.removeItem(self.globe.dryPlot)
        else:
            self.dryActive = True
            self.globe.draw_dryness()
            self.view.addItem(self.globe.dryPlot)



class Globe():
    def __init__(self, land, water):
        self.land = land
        self.water = water

    def draw_dryness(self):
        n = 20
        theta = np.linspace(0, 2*np.pi, n)
        phi = np.linspace(0, np.pi, n)

        vertex = []
        color = []
        for i in range(n):
            for j in range(1,n-1):
                x = self.land.x(self.r(theta[i], phi[j]), theta[i], phi[j])
                y = self.land.y(self.r(theta[i], phi[j]), theta[i], phi[j])
                z = self.land.z(self.r(theta[i], phi[j]), theta[i], phi[j])

                r = self.dryness(theta[i], phi[j])
                vertex.append([x, y, z])
                color.append([r, 0, 1-r])

        s = np.ones(len(color))*0.2
        c = np.array(color)
        c = c/c.max()
        v = np.array(vertex)
        self.dryPlot = gl.GLScatterPlotItem(pxMode=False)
        self.dryPlot.setData(pos=v, size=s, color=c)

    def temperature(self, theta, phi):
        if height(theta, phi) < 0:
            return np.cos(phi)**2 + 2
        else:
            return np.cos(phi)**2 + 2 - height(thetha, phi) - 0.5*np.sin(phi)**2*height(theta,phi)

    def lightness(self, theta, phi):
        return np.cos(phi)**2

    def dryness(self, theta, phi):
        if self.height(theta, phi) < 0:
            return 0

        dif = np.pi/20
        r = np.random.rand()
        return self.height(theta, phi) + self.dryness(theta + r*dif, phi + (1-r)*dif)

    def height(self, theta, phi):
        return self.land.r(theta, phi) - self.water.r(theta, phi)

    def r(self, theta, phi):
        return max(self.land.r(theta, phi), self.water.r(theta, phi))

class Surface():
    def __init__(self, irregular, radius, color):
        self.radius = radius
        self.a = np.random.beta(1,1,irregular)*np.pi*2
        self.b = np.random.beta(2,2,irregular)*np.pi

        n = 60
        theta = np.linspace(0, 2*np.pi, n)
        phi = np.linspace(0, np.pi, n)

        vertex = []
        face = []

        for i in range(n):
            for j in range(n):
                x = self.x(self.r(theta[i], phi[j]), theta[i], phi[j])
                y = self.y(self.r(theta[i], phi[j]), theta[i], phi[j])
                z = self.z(self.r(theta[i], phi[j]), theta[i], phi[j])
                vertex.append([x, y, z])

        for i in range(n-1):
            s = np.random.randint(n)
            for j in range(n-1):
                face.append([i*n + (s+j)%(n-1)+1, (i+1)*n + (s+j)%(n-1), (i+1)*n + (s+j)%(n-1)+1])
                face.append([i*n + (s+j)%(n-1), i*n + (s+j)%(n-1)+1, (i+1)*n + (s+j)%(n-1)])

        v = np.array(vertex)
        f = np.array(face)
        c = np.ones(f.shape)*color
        data = gl.MeshData(vertexes=v, faces=f, faceColors=c)
        self.mesh = gl.GLMeshItem(meshdata=data)
        self.mesh.setGLOptions(opts="translucent")

    def r(self, theta, phi):
        r = self.radius
        for i in range(len(self.a)):
            r += (-1)**i * np.exp(-(theta-self.a[i])**2*(phi-self.b[i])**2)
        return r

    def x(self, r, theta, phi):
        return r*np.cos(theta)*np.sin(phi)

    def y(self, r, theta, phi):
        return r*np.sin(theta)*np.sin(phi)

    def z(self, r, theta, phi):
        return r*np.cos(phi)

    def cart(self, r, theta, phi):
        return [self.x(r, theta, phi), self.y(r, theta, phi), self.z(r, theta, phi)]

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

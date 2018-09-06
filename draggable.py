import sys
import matplotlib
matplotlib.use("Qt5Agg")
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QWidget,QSizePolicy,QVBoxLayout,QHBoxLayout,QPushButton,QDialog,QFileDialog,QToolBar,QMessageBox, QLineEdit, QToolButton

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import numpy as np
from drag import DraggablePoint

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=10, height=8, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)
        self.parent = parent

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.lines = []
        self.list_points = []
        self.point_pairs = []
        self.number_of_lines = 0
        self.plot_line = False
        self.Qs = None
        self.couplings = None
        self.intercept = 0
        self.selected = []
        # self.plot()
        # self.create_draggable_points()

    def setParameter(self, Qs, couplings):
        self.Qs = Qs
        self.couplings = couplings


    def plot(self):
        #import numpy as np
        # axes = self.figure.add_subplot(111)
        x = np.asarray(self.couplings[:-1], dtype='float')
        Y = np.asarray(self.Qs[:-1], dtype='float')
        # #A = np.vstack([x, np.ones(len(x))]).T
        # #m, c = np.linalg.lstsq(A, Y, rcond=None)[0]
        # #axes.plot(x, Y, 'o', color = 'b', label='Original data', markersize=6)
        # #axes.plot(x, m*x + c, 'r', label='Fitted line')
        # axes.scatter(x, Y, color="blue", picker = 5, s=[50]*len(x))
        # axes.legend()
        # axes.set_title('Q')
        # self.draw()
        #print(x.min(), m*x.min()+c, x.max(), m*x.max()+c)
        #self.create_draggable_points(x.min(), m*x.min()+c, x.max(), m*x.max()+c, 0.1, 1000000)
        #testData = np.array([[0,0], [0.1, 0], [0, 0.3], [-0.4, 0], [0, -0.5]])
        ax = self.figure.add_subplot(111)
        ax.set_title('Calculate Q',fontsize=20)
        ax.set_xlabel('coupling %',fontsize=16)
        ax.set_ylabel('Q intrinsic',fontsize=16)
        coll = ax.scatter(x, Y, color=["blue"]*len(x), picker = 5, s=[50]*len(x))
        

        def on_pick(event):
            print(x[event.ind], Y[event.ind], "clicked")
            if [x[event.ind][0], Y[event.ind][0]] not in self.selected:                
                coll._facecolors[event.ind,:] = (1, 0, 0, 1)
                coll._edgecolors[event.ind,:] = (1, 0, 0, 1)
                self.selected.append([x[event.ind][0], Y[event.ind][0]])
            else:
                coll._facecolors[event.ind,:] = (0, 0, 1, 1)
                coll._edgecolors[event.ind,:] = (0, 0, 1, 1)
                self.selected.remove([x[event.ind][0], Y[event.ind][0]])
            self.figure.canvas.draw()
            print(self.selected)
        self.figure.canvas.mpl_connect('pick_event', on_pick)


    def create_draggable_points(self, x1, y1, x2, y2, xc, yc):
        self.list_points.append(DraggablePoint(self, True, x1, y1, 1, xc, yc))
        self.list_points.append(DraggablePoint(self, False, x2, y2, 1, xc, yc))
        # TODO Koordinaten an den Plot anpassen (+500)
        i = self.list_points[0]
        j = self.list_points[1]
        i.partner = j
        j.partner = i
        i.setLine(Line2D([i.x, j.x], [i.y, j.y], color='b', alpha=0.5))
        j.setLine(Line2D([i.x, j.x], [i.y, j.y], color='b', alpha=0.5))
        self.lines.append(i.line)
        self.lines.append(j.line)
        print(self.lines)

        self.point_pairs.append((i, j))
        
        self.updateFigure()
        i.drawline()
        j.drawline()

    def updateFigure(self):
        self.draw()

    def setIntercept(self, x1, y1, x2, y2):
        self.intercept = y1 - x1*(y2-y1)/(x2-x1)

    def updateQ(self):
        self.parent.updateQ(self.intercept)

    def Rsquared(self):
        if (self.selected == []):
            self.parent.alert(1)
        else:
            x = np.asarray([p[0] for p in self.selected], dtype='float')
            Y = np.asarray([p[1] for p in self.selected], dtype='float')
            A = np.vstack([x, np.ones(len(x))]).T
            m, c = np.linalg.lstsq(A, Y, rcond=None)[0]
            #axes.plot(x, Y, 'o', color = 'b', label='Original data', markersize=6)
            self.axes.plot(x, m*x + c, 'g', label='Fitted line')
            self.updateFigure()
            print(self.axes.lines)

    def unfit(self):
        if (self.axes.lines == []):
            self.parent.alert(2)
        else:
            self.axes.lines.pop()
            self.updateFigure()

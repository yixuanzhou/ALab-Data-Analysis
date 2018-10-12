import sys
import matplotlib
matplotlib.use("Qt5Agg")
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QSizePolicy

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import csv

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=2, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111, position=[0.2, 0.15, 0.65, 0.75])

        FigureCanvas.__init__(self, self.fig)
        self.parent = parent
        #FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        #FigureCanvas.updateGeometry(self)
        self.annot = None

        self.Qs = None
        self.couplings = None
        self.lambdas = None
        self.selected = []
        self.x = None
        self.Y = None
        self.coll = None
        self.mode = 1

    def setParameter(self, Qs, couplings, lambdas):
        self.Qs = Qs
        self.couplings = couplings
        self.lambdas = lambdas


    def plot(self, mode):
        self.mode = mode
        self.x = np.asarray(self.couplings[:], dtype='float')
        self.Y = np.asarray(self.Qs[:], dtype='float')
        self.annot = self.axes.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                                        va="top", ha="center",
                                        bbox=dict(boxstyle="round", fc="w"))
        self.annot.set_visible(False)
        self.axes.set_xlabel('coupling %',fontsize=12)
        self.axes.set_ylabel('Q intrinsic',fontsize=12)
        if (mode == 1):
            self.coll = self.axes.scatter(self.x, self.Y, color=["blue"]*len(self.x), marker='s', facecolor=[(0, 0, 0, 0)]*len(self.x), picker = 5, s=[50]*len(self.x))
        else:
            self.coll = self.axes.scatter(self.x, self.Y, color=["blue", "red"]*len(self.x), marker='s', facecolor=[(0, 0, 0, 0)]*len(self.x), picker = 5, s=[50]*len(self.x))
        self.figure.canvas.mpl_connect('pick_event', self.on_pick)
        self.figure.canvas.mpl_connect('motion_notify_event', self.on_hover)
        # print(self.x)
        # print(self.Y)

    def on_pick(self, event):
        if [self.x[event.ind][0], self.Y[event.ind][0]] not in self.selected:
            if self.mode == 1:
                self.coll._facecolors[event.ind,:] = (0, 0, 1, 1)
            else:
                if event.ind % 2 == 0:
                    self.coll._facecolors[event.ind,:] = (0, 0, 1, 1)
                else:
                    self.coll._facecolors[event.ind,:] = (1, 0, 0, 1)
            #self.coll._edgecolors[event.ind,:] = (1, 0, 0, 1)
            self.selected.append([self.x[event.ind][0], self.Y[event.ind][0]])
        else:
            self.coll._facecolors[event.ind,:] = (0, 0, 0, 0)
            #self.coll._edgecolors[event.ind,:] = (0, 0, 1, 1)
            self.selected.remove([self.x[event.ind][0], self.Y[event.ind][0]])
        self.figure.canvas.draw()
        #print(self.selected)
        #self.figure.canvas.mpl_connect('pick_event', on_pick)      

    def update_annot(self, ind):
        pos = self.coll.get_offsets()[ind["ind"][0]]
        self.annot.xy = pos
        text = "{}, {}, {}".format(" ".join([str('%s' % float('%.8g' % self.lambdas[n])) for n in ind["ind"]]),
                               " ".join([str('%s' % float('%.4g' % self.x[n])) for n in ind["ind"]]), 
                               " ".join([str('{:.3e}'.format(self.Y[n])) for n in ind["ind"]]))
        self.annot.set_text(text)

    def on_hover(self, event):
        vis = self.annot.get_visible()
        if event.inaxes == self.axes:
            cont, ind = self.coll.contains(event)
            if cont:
                self.update_annot(ind)
                self.annot.set_visible(True)
                self.figure.canvas.draw_idle()
            else:
                if vis:
                    self.annot.set_visible(False)
                    self.figure.canvas.draw_idle()

    def updateFigure(self):
        self.draw()

    def updateQ(self, intercept):
        self.parent.updateQ(intercept, std_err)

    def export(self):
        print(self.Qs)
        with open("./result", "w") as output:
            writer = csv.writer(output, lineterminator='\n')
            writer.writerows(self.Qs)

    def Rsquared(self):
        if (self.selected == []):
            self.parent.alert(1)
        else:
            x = np.asarray([p[0] for p in self.selected], dtype='float')
            Y = np.asarray([p[1] for p in self.selected], dtype='float')
            A = np.vstack([x, np.ones(len(x))]).T
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, Y)
            #axes.plot(x, Y, 'o', color = 'b', label='Original data', markersize=6)
            self.axes.plot(x, slope*x + intercept, 'g', label='Fitted line')
            self.updateFigure()
            self.parent.updateQ(intercept, std_err)
            print(self.axes.lines)

    def unfit(self):
        if (self.axes.lines == []):
            self.parent.alert(2)
        else:
            self.axes.lines.pop()
            self.updateFigure()

    def reset(self):
        self.fig.clear()
        self.axes = self.fig.add_subplot(111, position=[0.2, 0.15, 0.65, 0.75])
        self.figure.canvas.mpl_disconnect(self.on_pick)
        self.figure.canvas.mpl_disconnect(self.on_hover)
        self.Qs = None
        self.couplings = None
        self.intercept = 0
        self.selected.clear()
        self.updateFigure()

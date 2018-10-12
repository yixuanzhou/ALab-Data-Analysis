import sys
from PyQt5 import QtWidgets, QtGui
 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
 
import numpy as np
from calculateQ import parse_info
 
class Graph(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Graph, self).__init__(parent)
 
        self.figure = plt.figure(figsize=(4, 3))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111, position=[0.2, 0.15, 0.65, 0.75]) 
         
        self.toolbar = NavigationToolbar(self.canvas, self) 

        self.q1_valley = []
 
        # set the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)


    def zoom_fun(self, event):
        base_scale = 1.5
        # get the current x and y limits
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()
        cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
        cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5
        xdata = event.xdata # get event x location
        ydata = event.ydata # get event y location
        if event.button == 'up':
            # deal with zoom in
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            # deal with zoom out
            scale_factor = base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
            #print event.button
        # set new limits
        self.ax.set_xlim([xdata - cur_xrange*scale_factor,
                     xdata + cur_xrange*scale_factor])
        self.ax.set_ylim([ydata - cur_yrange*scale_factor,
                     ydata + cur_yrange*scale_factor])
        self.canvas.draw() # force re-draw
         
    def plot(self, q1):
        ''' plot some random stuff '''
        q1 = q1.ravel()
        valley_index = np.argmin(q1)
        self.q1_valley = q1[valley_index-5000:valley_index+5000]
        #plt.plot(q1_valley)
        #self.ax.hold(False)
        self.ax.plot(self.q1_valley)
        self.canvas.draw()
        #fig = ax.get_figure() # get the figure of interest
        # attach the call back
        self.figure.canvas.mpl_connect('scroll_event', self.zoom_fun)

    def calcRange(self):
        mean = np.average(self.q1_valley)
        self.q1_valley = -1 * self.q1_valley + mean
        from lmfit.models import GaussianModel
        mod = GaussianModel()
        x = np.asarray(list(range(0,10000)))
        pars = mod.guess(self.q1_valley, x=x)
        out = mod.fit(self.q1_valley, pars, x=x)

        res = out.fit_report()
        info = res.split("\n")
        variables = parse_info(info, 1)

        width = variables['fwhm']
        print(width)
        return float(width)
 
    def reset(self):
        self.figure.clear()
        self.ax = self.figure.add_subplot(111, position=[0.2, 0.15, 0.65, 0.75])
        self.figure.canvas.mpl_disconnect(self.zoom_fun)
        self.canvas.draw()
# -*- coding: utf-8 -*-
__author__ = 'yixuanzhou'

import sys
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QPainterPath, QFont
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from calculateQ import baseQ
from draggable import PlotCanvas

class Window(QWidget):
    """Whole structure"""
    def __init__(self):
        super(Window, self).__init__()
        #self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("Q")
        self.setStyleSheet(open("QSS/window.qss", "r").read())
        self.resize(800, 600)

        self.mainWindow = MainWindow(self)
        self.mainContents = QTabWidget()

        self.mainContents = QTabWidget()
        self.mainContents.tabBar().setObjectName("mainTab")
        self.setContents()
        self.setLayouts()

    def setContents(self, index=0):        
        self.mainContents.addTab(self.mainWindow, '')
        self.setLayouts()

    def setLayouts(self):
        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.mainContents)
        
        # self.mainLayout.setStretch(0, 60)
        # self.mainLayout.setStretch(1, 400)

        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.mainLayout)


class MainWindow(QFrame):
    canvas = None

    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        
        self.setObjectName('Main')
        self.setStyleSheet(open("QSS/mainwindow.qss", "r").read())
        
        self.parent = parent

        self.setButtons()
        self.setLabels()
        self.setLayouts()

    def setButtons(self):
        ''' Set all buttons here. '''
        self.Load = QPushButton(self) # PushButton 'Load'
        self.Load.setText(u"Open")
        self.Load.setFixedWidth(90)
        self.Load.clicked.connect(self.openQ)

        self.Run = QPushButton(self) # PushButton 'Run'
        self.Run.setText(u"Load")
        self.Run.setFixedWidth(90)
        self.Run.clicked.connect(self.process)

        self.Fit = QPushButton(self) # PushButton 'Run'
        self.Fit.setText(u"Fit")
        self.Fit.setFixedWidth(90)
        self.Fit.clicked.connect(self.fit)

        self.Export = QPushButton(self)
        self.Export.setText(u"Export")
        self.Export.setFixedWidth(90)
        #self.Export.clicked.connect(self.resetwindow)

        self.Reset = QPushButton(self)
        self.Reset.setText(u"Reset")
        self.Reset.setFixedWidth(90)
        self.Reset.clicked.connect(self.reset)

        self.Unfit = QPushButton(self) # PushButton 'Run'
        self.Unfit.setText(u"Unfit")
        self.Unfit.setFixedWidth(90)
        self.Unfit.clicked.connect(self.unfit)
     
    def setLabels(self):
        ''' Set all labels here. '''
        self.modulation = QLabel(self)
        self.modulation.setText("Modulation Coefficient:")
        self.comboBox = QComboBox(self)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("Red")
        self.comboBox.addItem("Purple")
        self.comboBox.addItem("Gary")
        self.comboBox.addItem("Black")
        self.comboBox.addItem("Green")
        self.comboBox.addItem("Blue")
        self.comboBox.addItem("Orange")
        self.comboBox.addItem("white")
        self.comboBox.addItem("Pink")
        self.comboBox.addItem("Yellow")

        self.lambda_tag = QLabel(self)
        self.lambda_tag.setText("Starting lambda:")
        self.slambda = QLineEdit()
        # self.slope.setValidator(QIntValidator())
        self.slambda.setText("1572.42")
        self.slambda.setAlignment(Qt.AlignRight)

        self.slope_tag = QLabel(self)
        self.slope_tag.setText("Slope:")
        self.slope = QLineEdit()
        # self.slope.setValidator(QIntValidator())
        self.slope.setText("396.5")
        self.slope.setAlignment(Qt.AlignRight)
      
        self.result = QLabel(self) # Label 'Output_image'
        self.result.setObjectName("OutputImg")
        self.result.setFixedHeight(25)   
        self.result.setFixedWidth(100)        

    def setLayouts(self):
        ''' Set layout here. '''
        self.mainLayout = QVBoxLayout()
        self.labelLayout = QHBoxLayout()
        self.resultLayout = QHBoxLayout()
        self.drawLayout = QGridLayout()
        
        self.buttonLayout = QHBoxLayout()
        self.functionLayout = QHBoxLayout()

        self.labelLayout.addWidget(self.modulation, 0, Qt.AlignCenter)
        self.labelLayout.addWidget(self.comboBox, 0, Qt.AlignCenter)
        self.labelLayout.addWidget(self.lambda_tag, 0, Qt.AlignCenter)
        self.labelLayout.addWidget(self.slambda, 0, Qt.AlignCenter)
        self.labelLayout.addWidget(self.slope_tag, 0, Qt.AlignCenter)
        self.labelLayout.addWidget(self.slope, 0, Qt.AlignCenter)

        self.resultLayout.addWidget(self.result, 0, Qt.AlignCenter)

        self.canvas = PlotCanvas(self, width=10, height=8)
        self.drawLayout.addWidget(self.canvas, 0, 0, 5, 1)

        # Button layout
        self.buttonLayout.addWidget(self.Load, 0, Qt.AlignCenter)
        self.buttonLayout.addWidget(self.Run, 0, Qt.AlignCenter)
        self.buttonLayout.addWidget(self.Fit, 0, Qt.AlignCenter)


        # Result layout
        self.functionLayout.addWidget(self.Export, 0, Qt.AlignCenter)
        self.functionLayout.addWidget(self.Reset, 0, Qt.AlignCenter)
        self.functionLayout.addWidget(self.Unfit, 0, Qt.AlignCenter)

        self.mainLayout.addLayout(self.labelLayout)
        self.mainLayout.addSpacing(20)
        self.mainLayout.addLayout(self.resultLayout)
        self.mainLayout.addLayout(self.drawLayout)
        self.mainLayout.addSpacing(60)
        self.mainLayout.addLayout(self.buttonLayout)
        self.mainLayout.addLayout(self.functionLayout)
     
        self.setLayout(self.mainLayout)

    def reset(self):
        self.canvas.plot()

    def openQ(self):
        global Qname
        Qname, _ = QFileDialog.getOpenFileName(self, "Open lvm File", "", " *.lvm;;All Files (*)")
        print(Qname)

    def process(self):
        Qs, couplings = baseQ(Qname, self.slambda.text(), self.slope.text(), self.comboBox.currentText())
        self.canvas.setParameter(Qs, couplings)
        self.canvas.plot()
        self.canvas.updateFigure()
        # import numpy as np
        # x = np.asarray(couplings[:-1], dtype='float')
        # Y = np.asarray(Qs[:-1], dtype='float')
        # A = np.vstack([x, np.ones(len(x))]).T
        # m, c = np.linalg.lstsq(A, Y, rcond=None)[0]
        # self.canvas.create_draggable_points(x.min(), m*x.min()+c, x.max(), m*x.max()+c, 0.1, 1000000)

    def fit(self):
        self.canvas.Rsquared()

    def unfit(self):
        self.canvas.unfit()

    def updateQ(self, intercept):
        self.result.setText(str(intercept))

    def alert(self, num):
        if (num == 1): QMessageBox.about(self, "Error", "No point selected")
        if (num == 2): QMessageBox.about(self, "Error", "You should fit first")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Window()
    main.show()
    sys.exit(app.exec_())